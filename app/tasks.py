import os
import requests

from datetime import datetime
from flask import current_app, render_template
from flask_mail import Message

from . import celery, create_app, mail, models


@celery.task
def send_email(recipients, subject, body, html=None, config={}, **kwargs):
    app = create_app(os.getenv("APP_CONFIG", "default"))

    attachments = kwargs.pop("attachments", [])
    with app.app_context():
        default_sender = current_app.config["APP_MAIL_SENDER"]
        sender = config.get("sender", default_sender)
        message = Message(subject, sender=sender, recipients=recipients, **kwargs)
        message.body = body
        message.html = body
        if html:
            message.html = html

        for item in attachments:
            with app.open_resource(item) as f:
                message.attach(f.read())
        mail.send(message)
