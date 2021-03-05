import os

from flask import current_app, render_template
from flask_mail import Message

from . import celery, create_app, mail


@celery.task
def send_async_email(to, subject, body, html, sender):
    app = create_app(os.getenv("APP_CONFIG", "default"))
    message = Message(subject, sender=sender, recipients=to)
    message.body = body
    message.html = html
    with app.app_context():
        mail.send(message)


def send_email(to, subject, template, **kwargs):
    if not isinstance(to, list):
        to = [to]
    body = render_template("{}.txt".format(template), **kwargs)
    html = render_template("{}.jinja".format(template), **kwargs)
    sender = current_app.config["APP_MAIL_SENDER"]
    send_async_email.delay(to, subject, body, html, sender)
