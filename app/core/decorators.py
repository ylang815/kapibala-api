import functools
import asyncio
from typing import Callable
import logging

logger = logging.getLogger(__name__)

def async_mail_notify(subject: str = None, body: str = None):
    """
    异步邮件通知装饰器
    :param subject: 邮件主题，如果为None则使用默认主题
    :param body: 邮件内容模板，可以使用 {result} 引用原函数返回值
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 执行原始函数
                result = func(*args, **kwargs)
                
                # 异步发送邮件
                async def send_mail_task():
                    from app.services.mail_service import mail_service
                    try:
                        # 构建邮件内容
                        actual_subject = subject or f"系统通知 - {func.__name__}"
                        actual_body = body.format(result=result) if body else str(result)
                        
                        await asyncio.to_thread(
                            mail_service.send_notification,
                            subject=actual_subject,
                            body=actual_body
                        )
                    except Exception as e:
                        logger.error(f"异步发送邮件失败: {str(e)}")
                
                # 创建异步任务
                asyncio.create_task(send_mail_task())
                
                return result
            except Exception as e:
                logger.error(f"函数执行失败: {str(e)}")
                raise e
        return wrapper
    return decorator 