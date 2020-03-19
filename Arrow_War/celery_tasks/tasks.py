from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Arrow_War.settings')
django.setup()




# redis数据库1是session缓存，2为celery
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/2')

@app.task
def send_register_active_email(user_id, user_email, user_username):
    # 创建加密实例
    serializer = Serializer(settings.SECRET_KEY, 300)
    info = {'user_id':user_id}
    token = serializer.dumps(info)
    token = token.decode()

    # 发送激活邮件, 包含激活链接:http://127.0.0.1:8000/users/active/3
    subject = 'Arrows_War'  # 欢迎信息
    message = '' # 邮件正文
    sender = settings.EMAIL_FROM
    receiver = [user_email]
    html_message = '<h1>%s,欢迎您注册Arrow_War</h1><br/><a href="http://127.0.0.1:8000/users/active/%s">请点击此处来激活您的账户</a>'%(user_username, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)