import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging
import traceback

logger = logging.getLogger(__name__)

class MailService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.mail_from = settings.MAIL_FROM
        self.mail_to = settings.MAIL_TO

    def send_mail(self, subject: str, body: str, html: bool = False) -> bool:
        """
        发送邮件
        :param subject: 邮件主题
        :param body: 邮件内容
        :param html: 是否为HTML格式
        :return: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.mail_from
            msg['To'] = self.mail_to
            msg['Subject'] = subject

            # 设置邮件内容
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))

            # 创建SSL上下文
            context = ssl.create_default_context()

            # 使用SSL连接QQ邮箱SMTP服务器
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
                return True
        except Exception as e:
            error_msg = f"邮件发送失败: {e.__class__.__name__} - {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def send_notification(self, subject: str, body: str) -> bool:
        """
        发送通知邮件的快捷方法
        :param subject: 通知标题
        :param body: 通知内容
        :return: 是否发送成功
        """
        html_content = f"""
        <html>
            <body>
                <h2>{subject}</h2>
                <p>{body}</p>
                <hr>
                <p><small>来自卡皮巴拉的通知邮件</small></p>
            </body>
        </html>
        """
        return self.send_mail(subject, body, html=True)

mail_service = MailService()