# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from conf import settings

def send_mail(mail_account, contact, content):
    smtp_obj = smtplib.SMTP(settings.opt['EMAIL']['HOST'], settings.opt['EMAIL']['PORT'])
    # self.smtp_obj.set_debuglevel(1)
    smtp_obj.starttls() 
    smtp_obj.login(settings.opt['EMAIL']['ACCOUNT'], settings.opt['EMAIL']['PASSWORD'])

    sender = '{0}@{1}'.format(settings.opt['EMAIL']['ACCOUNT'], 
            settings.opt['EMAIL']['POSTFIX'])
    receivers = [mail_account]
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    text = u'尊敬的{0}, 您好： \r\n\r\n{1}'.format(contact, content)
    message = MIMEText(text, 'plain', 'utf-8')
    # message['From'] = 'game.ksyun<{0}>'.format(sender)
    message['From'] = u'金山游戏云移动端网络监控<{0}>'.format(sender)
    message['To'] =  Header(''.join(receivers), 'utf-8')
    message['Subject'] = Header(u'移动端网络监控告警通知', 'utf-8')
    smtp_obj.sendmail(sender, receivers, message.as_string())
    smtp_obj.quit()
