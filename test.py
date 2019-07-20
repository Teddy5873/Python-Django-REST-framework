from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = '58730548@qq.com'
#在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'tonprviqeixzcada'
#收件人看到的发件人
EMAIL_FROM = 'Blackpink_Lisa<58730548@qq.com>'

subject = "Blackpink_Lisa"
mail = ['979463854@qq.com',]
message ='我喜欢你男朋友，可是他爱你'

send_mail(subject,'',EMAIL_FROM,mail,html_message=message)