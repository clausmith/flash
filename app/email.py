from flask import current_app, render_template

from .tasks import send_email


def send_email_template(to, subject, template, **kwargs):
    if not isinstance(to, list):
        to = [to]
    body = render_template("{}.txt".format(template), **kwargs)
    html = render_template("{}.html".format(template), **kwargs)
    send_email.delay(to, subject, body, html)
