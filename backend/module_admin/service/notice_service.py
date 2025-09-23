import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.dao.notice_dao import NoticeDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.notice_vo import DeleteNoticeModel, NoticeModel, NoticePageQueryModel
from utils.common_util import CamelCaseUtil
from module_redfish.core.realtime_service import RealtimePushService
from utils.log_util import logger


class NoticeService:
    """
    通知公告管理模块服务层
    """

    @classmethod
    async def get_notice_list_services(
        cls, query_db: AsyncSession, query_object: NoticePageQueryModel, is_page: bool = True
    ):
        """
        获取通知公告列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 通知公告列表信息对象
        """
        notice_list_result = await NoticeDao.get_notice_list(query_db, query_object, is_page)

        return notice_list_result

    @classmethod
    async def check_notice_unique_services(cls, query_db: AsyncSession, page_object: NoticeModel):
        """
        校验通知公告是否存在service

        :param query_db: orm对象
        :param page_object: 通知公告对象
        :return: 校验结果
        """
        notice_id = -1 if page_object.notice_id is None else page_object.notice_id
        notice = await NoticeDao.get_notice_detail_by_info(query_db, page_object)
        if notice and notice.notice_id != notice_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_notice_services(cls, query_db: AsyncSession, page_object: NoticeModel):
        """
        新增通知公告信息service

        :param query_db: orm对象
        :param page_object: 新增通知公告对象
        :return: 新增通知公告校验结果
        """
        if not await cls.check_notice_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增通知公告{page_object.notice_title}失败，通知公告已存在')
        else:
            try:
                # 添加通知到数据库
                result = await NoticeDao.add_notice_dao(query_db, page_object)
                
                # 在commit之前准备推送数据（避免commit后访问数据库会话）
                notice_data = None
                if page_object.status == '0':  # 只推送正常状态的通知
                    notice_data = {
                        "notice_id": result.notice_id,
                        "notice_title": page_object.notice_title,
                        "notice_type": page_object.notice_type,
                        "create_by": page_object.create_by,
                        "create_time": page_object.create_time.isoformat() if page_object.create_time else None,
                        "status": page_object.status
                    }
                
                # 提交事务
                await query_db.commit()
                
                # 事务提交后异步推送WebSocket消息
                if notice_data:
                    logger.info(f"[Notice] 准备推送新通知: {notice_data}")
                    # 使用asyncio.create_task异步执行推送，完全独立于数据库会话
                    asyncio.create_task(
                        RealtimePushService.push_notice_notification(notice_data, "notice_published")
                    )
                    logger.info(f"[Notice] WebSocket推送任务已创建")
                
                return CrudResponseModel(is_success=True, message='新增成功')
            except Exception as e:
                await query_db.rollback()
                raise e

    @classmethod
    async def edit_notice_services(cls, query_db: AsyncSession, page_object: NoticeModel):
        """
        编辑通知公告信息service

        :param query_db: orm对象
        :param page_object: 编辑通知公告对象
        :return: 编辑通知公告校验结果
        """
        edit_notice = page_object.model_dump(exclude_unset=True)
        notice_info = await cls.notice_detail_services(query_db, page_object.notice_id)
        if notice_info.notice_id:
            if not await cls.check_notice_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改通知公告{page_object.notice_title}失败，通知公告已存在')
            else:
                try:
                    # 保存旧状态用于判断是否需要推送
                    old_status = notice_info.status
                    
                    # 更新通知信息
                    await NoticeDao.edit_notice_dao(query_db, edit_notice)
                    
                    # 在commit之前准备推送数据（避免commit后访问数据库会话）
                    new_status = page_object.status if page_object.status is not None else old_status
                    notice_data = None
                    
                    # 如果通知状态变为正常（从关闭到正常）或者是正常状态的内容更新，准备推送数据
                    if (old_status == '1' and new_status == '0') or (new_status == '0'):
                        notice_data = {
                            "notice_id": page_object.notice_id,
                            "notice_title": page_object.notice_title or notice_info.notice_title,
                            "notice_type": page_object.notice_type or notice_info.notice_type,
                            "create_by": notice_info.create_by,
                            "create_time": notice_info.create_time.isoformat() if notice_info.create_time else None,
                            "update_time": page_object.update_time.isoformat() if page_object.update_time else None,
                            "status": new_status
                        }
                        action = "notice_published" if old_status == '1' and new_status == '0' else "notice_updated"
                    
                    # 提交事务
                    await query_db.commit()
                    
                    # 事务提交后异步推送WebSocket消息
                    if notice_data:
                        # 使用asyncio.create_task异步执行推送，完全独立于数据库会话
                        asyncio.create_task(
                            RealtimePushService.push_notice_notification(notice_data, action)
                        )
                    
                    return CrudResponseModel(is_success=True, message='更新成功')
                except Exception as e:
                    await query_db.rollback()
                    raise e
        else:
            raise ServiceException(message='通知公告不存在')

    @classmethod
    async def delete_notice_services(cls, query_db: AsyncSession, page_object: DeleteNoticeModel):
        """
        删除通知公告信息service

        :param query_db: orm对象
        :param page_object: 删除通知公告对象
        :return: 删除通知公告校验结果
        """
        if page_object.notice_ids:
            notice_id_list = page_object.notice_ids.split(',')
            try:
                for notice_id in notice_id_list:
                    await NoticeDao.delete_notice_dao(query_db, NoticeModel(noticeId=notice_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入通知公告id为空')

    @classmethod
    async def notice_detail_services(cls, query_db: AsyncSession, notice_id: int):
        """
        获取通知公告详细信息service

        :param query_db: orm对象
        :param notice_id: 通知公告id
        :return: 通知公告id对应的信息
        """
        notice = await NoticeDao.get_notice_detail_by_id(query_db, notice_id=notice_id)
        if notice:
            result = NoticeModel(**CamelCaseUtil.transform_result(notice))
        else:
            result = NoticeModel(**dict())

        return result
