"""
连通性集成测试
测试DeviceMonitor中的业务IP连通性检查功能
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from module_redfish.core.device_monitor import DeviceMonitor
from module_redfish.service.connectivity_service import ConnectivityService


class TestConnectivityIntegration:
    """连通性集成测试"""
    
    def setup_method(self):
        """测试初始化"""
        self.monitor = DeviceMonitor()
        self.device_info = {
            'device_id': 1,
            'hostname': 'test-server',
            'business_ip': '192.168.1.100',
            'oob_ip': '192.168.1.101',
            'oob_port': 443,
            'business_type': '生产系统',
            'redfish_username': 'admin',
            'redfish_password': 'password123'
        }
        self.status_data = {
            'system_info': {'Status': {'Health': 'OK', 'State': 'Enabled'}},
            'processors': [],
            'memory': [],
            'storage': [],
            'power': [],
            'temperatures': [],
            'fans': []
        }
    
    @pytest.mark.asyncio
    async def test_connectivity_online_generates_ok_component(self):
        """测试设备在线时生成OK状态的connectivity组件"""
        # Mock ConnectivityService返回在线状态
        mock_connectivity_result = {
            'online': True,
            'hostname': 'test-server',
            'business_ip': '192.168.1.100',
            'check_duration_ms': 50.0,
            'ping': {'success': True, 'method': 'ping'},
            'check_time': datetime.now().isoformat()
        }
        
        with patch.object(ConnectivityService, 'check_device_business_ip_connectivity', 
                         new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_connectivity_result
            
            alerts, all_components = await self.monitor._analyze_status(
                self.device_info, self.status_data
            )
            
            # 验证调用参数
            mock_check.assert_called_once_with(db=None, business_ip='192.168.1.100')
            
            # 验证生成的组件状态
            connectivity_components = [c for c in all_components if c['component_type'] == 'connectivity']
            assert len(connectivity_components) == 1
            
            connectivity_component = connectivity_components[0]
            assert connectivity_component['component_type'] == 'connectivity'
            assert connectivity_component['component_name'] == '宕机'
            assert connectivity_component['health_status'] == 'ok'
            
            # 验证不生成告警
            connectivity_alerts = [a for a in alerts if a['component_type'] == 'connectivity']
            assert len(connectivity_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_connectivity_offline_generates_critical_component_and_alert(self):
        """测试设备离线时生成Critical状态的connectivity组件和告警"""
        # Mock ConnectivityService返回离线状态
        mock_connectivity_result = {
            'online': False,
            'hostname': 'test-server',
            'business_ip': '192.168.1.100',
            'check_duration_ms': 3000.0,
            'ping': {'success': False, 'method': 'ping', 'error': 'Request timeout'},
            'check_time': datetime.now().isoformat(),
            'error': 'Connection timeout'
        }
        
        with patch.object(ConnectivityService, 'check_device_business_ip_connectivity', 
                         new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_connectivity_result
            
            alerts, all_components = await self.monitor._analyze_status(
                self.device_info, self.status_data
            )
            
            # 验证生成的组件状态
            connectivity_components = [c for c in all_components if c['component_type'] == 'connectivity']
            assert len(connectivity_components) == 1
            
            connectivity_component = connectivity_components[0]
            assert connectivity_component['component_type'] == 'connectivity'
            assert connectivity_component['component_name'] == '宕机'
            assert connectivity_component['health_status'] == 'critical'
            
            # 验证生成告警
            connectivity_alerts = [a for a in alerts if a['component_type'] == 'connectivity']
            assert len(connectivity_alerts) == 1
            
            connectivity_alert = connectivity_alerts[0]
            assert connectivity_alert['device_id'] == 1
            assert connectivity_alert['alert_source'] == 'connectivity'
            assert connectivity_alert['component_type'] == 'connectivity'
            assert connectivity_alert['component_name'] == '宕机'
            assert connectivity_alert['health_status'] == 'critical'
            assert connectivity_alert['urgency_level'] == 'urgent'
            assert 'unreachable' in connectivity_alert['alert_message']
            assert '192.168.1.100' in connectivity_alert['alert_message']
    
    @pytest.mark.asyncio
    async def test_connectivity_check_exception_generates_unknown_component(self):
        """测试连通性检查异常时生成unknown状态的connectivity组件"""
        # Mock ConnectivityService抛出异常
        with patch.object(ConnectivityService, 'check_device_business_ip_connectivity', 
                         new_callable=AsyncMock) as mock_check:
            mock_check.side_effect = Exception("Network error")
            
            alerts, all_components = await self.monitor._analyze_status(
                self.device_info, self.status_data
            )
            
            # 验证生成的组件状态
            connectivity_components = [c for c in all_components if c['component_type'] == 'connectivity']
            assert len(connectivity_components) == 1
            
            connectivity_component = connectivity_components[0]
            assert connectivity_component['component_type'] == 'connectivity'
            assert connectivity_component['component_name'] == '宕机'
            assert connectivity_component['health_status'] == 'unknown'
            
            # 验证不生成告警
            connectivity_alerts = [a for a in alerts if a['component_type'] == 'connectivity']
            assert len(connectivity_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_no_business_ip_skips_connectivity_check(self):
        """测试没有业务IP时跳过连通性检查"""
        # 移除business_ip
        device_info_no_ip = self.device_info.copy()
        device_info_no_ip['business_ip'] = None
        
        with patch.object(ConnectivityService, 'check_device_business_ip_connectivity', 
                         new_callable=AsyncMock) as mock_check:
            alerts, all_components = await self.monitor._analyze_status(
                device_info_no_ip, self.status_data
            )
            
            # 验证未调用连通性检查
            mock_check.assert_not_called()
            
            # 验证没有生成connectivity组件
            connectivity_components = [c for c in all_components if c['component_type'] == 'connectivity']
            assert len(connectivity_components) == 0
    
    @pytest.mark.asyncio
    async def test_connectivity_check_with_other_components(self):
        """测试连通性检查与其他组件状态检查的集成"""
        # 添加一个有问题的处理器
        status_data_with_issues = self.status_data.copy()
        status_data_with_issues['processors'] = [
            {'Status': {'Health': 'Critical', 'State': 'Enabled'}, 'socket': 'CPU1'}
        ]
        
        # Mock连通性检查返回离线
        mock_connectivity_result = {
            'online': False,
            'hostname': 'test-server',
            'business_ip': '192.168.1.100',
            'error': 'Connection timeout'
        }
        
        with patch.object(ConnectivityService, 'check_device_business_ip_connectivity', 
                         new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_connectivity_result
            
            alerts, all_components = await self.monitor._analyze_status(
                self.device_info, status_data_with_issues
            )
            
            # 验证生成了connectivity组件
            connectivity_components = [c for c in all_components if c['component_type'] == 'connectivity']
            assert len(connectivity_components) == 1
            assert connectivity_components[0]['health_status'] == 'critical'
            
            # 验证生成了processor组件
            processor_components = [c for c in all_components if c['component_type'] == 'processor']
            assert len(processor_components) == 1
            assert processor_components[0]['health_status'] == 'critical'
            
            # 验证生成了两个告警
            connectivity_alerts = [a for a in alerts if a['component_type'] == 'connectivity']
            processor_alerts = [a for a in alerts if a['component_type'] == 'processor']
            assert len(connectivity_alerts) == 1
            assert len(processor_alerts) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 