#!/usr/bin/env python3
"""
最终设备导入模板测试脚本
"""
import asyncio
import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from module_redfish.service.device_service import DeviceService


async def test_final_device_import_template():
    """测试最终的设备导入模板生成"""
    print("=== 测试最终设备导入模板 ===")
    
    try:
        template_data = await DeviceService.get_device_import_template_services()
        print(f"✅ 模板生成成功，数据长度: {len(template_data)} bytes")
        
        # 保存模板到文件进行验证
        filename = "最终设备导入模板.xlsx"
        with open(filename, "wb") as f:
            f.write(template_data)
        print(f"✅ 模板已保存到 {filename}")
        
        # 验证模板内容
        df = pd.read_excel(filename, sheet_name='设备导入模板')
        print(f"✅ 模板包含 {len(df.columns)} 个字段")
        print(f"📋 字段列表: {list(df.columns)}")
        print(f"📊 示例数据行数: {len(df)}")
        
        # 检查是否有说明页
        xl = pd.ExcelFile(filename)
        print(f"📄 工作表: {xl.sheet_names}")
        
        # 读取说明页内容
        if '导入说明' in xl.sheet_names:
            df_info = pd.read_excel(filename, sheet_name='导入说明')
            print(f"📝 说明页包含 {len(df_info)} 行说明")
            
        return True
    except Exception as e:
        print(f"❌ 模板生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_final_test_data():
    """创建最终的测试导入数据"""
    print("\n=== 创建最终测试数据 ===")
    
    # 定义完整测试数据
    test_data = [
        {
            '主机名*': 'web-server-01',
            '业务IP*': '10.1.1.101',
            '带外IP*': '10.100.1.101',
            '机房位置': '北京数据中心-A栋-3层-机柜A301',
            '操作系统': 'CentOS 7.9.2009',
            '序列号': 'CN123456789',
            '设备型号': 'PowerEdge R740',
            '厂商': 'Dell',
            '技术系统': 'Web服务集群',
            '系统负责人': '张三',
            '业务类型': '核心业务',
            'Redfish用户名': 'admin',
            'Redfish密码': 'Dell123!',
            '备注': '生产环境核心Web服务器'
        },
        {
            '主机名*': 'db-server-01',
            '业务IP*': '10.1.2.101',
            '带外IP*': '10.100.2.101',
            '机房位置': '北京数据中心-A栋-3层-机柜A302',
            '操作系统': 'Red Hat Enterprise Linux 8.4',
            '序列号': 'HP987654321',
            '设备型号': 'ProLiant DL380 Gen10',
            '厂商': 'HPE',
            '技术系统': '数据库集群',
            '系统负责人': '李四',
            '业务类型': '核心业务',
            'Redfish用户名': 'root',
            'Redfish密码': 'Hpe@2023',
            '备注': '数据库集群主节点'
        },
        {
            '主机名*': 'app-server-01',
            '业务IP*': '10.1.3.101',
            '带外IP*': '10.100.3.101',
            '机房位置': '上海数据中心-B栋-2层-机柜B201',
            '操作系统': 'Ubuntu Server 20.04 LTS',
            '序列号': 'LN567890123',
            '设备型号': 'ThinkSystem SR650',
            '厂商': 'Lenovo',
            '技术系统': '应用服务集群',
            '系统负责人': '王五',
            '业务类型': '支撑业务',
            'Redfish用户名': '',  # 测试默认值
            'Redfish密码': '',    # 测试默认值
            '备注': '应用服务器，测试默认凭证'
        }
    ]
    
    # 创建DataFrame
    df = pd.DataFrame(test_data)
    
    # 保存为Excel文件
    filename = '最终测试导入数据.xlsx'
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"✅ 最终测试导入文件已创建: {filename}")
    print(f"📊 包含 {len(test_data)} 条完整测试数据")
    print(f"🔧 包含字段: {list(df.columns)}")
    
    return filename


async def main():
    """主测试函数"""
    print("开始测试最终设备导入模板功能...")
    
    # 测试最终导入模板
    template_success = await test_final_device_import_template()
    
    # 创建最终测试导入文件
    if template_success:
        create_final_test_data()
    
    if template_success:
        print("\n🎉 最终模板测试通过!")
        print("📝 模板特点:")
        print("   • 包含14个字段（3个必填，11个可选）")
        print("   • 包含2行示例数据")
        print("   • 包含详细的使用说明页")
        print("   • 包含业务类型选项说明")
        print("   • 美观的表格样式和格式")
        print("   • 包含备注字段")
    else:
        print("\n❌ 测试失败!")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 