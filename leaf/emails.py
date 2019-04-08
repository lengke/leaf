from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from leaf.ext import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['LEAP_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_confirm_email(user, token, to=None):
    send_mail(subject='验证邮箱地址', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject='重置密码', to=user.email, template='emails/reset_password', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject='修改邮箱地址', to=to or user.email, template='emails/change_email', user=user, token=token)


# 上传新文件后自动发邮件给项目成员
# def send_upload_file_email(user, to=None):
#     send_mail(subject='验证邮箱地址', to=to or user.email, template='emails/confirm', user=user, token=token)

# 添加项目成员后自动发邮件给被添加者
# def send_add_new_member_email(user, to=None):
#     send_mail(subject='验证邮箱地址', to=to or user.email, template='emails/confirm', user=user, token=token)

