import pytz

from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from flask import (
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import login_required, current_user
from random import shuffle
from sqlalchemy import and_, func, inspect, or_
from webargs.flaskparser import use_args
from werkzeug import SharedDataMiddleware

from .. import db, models, tasks
from ..email import send_email_template
from ..exceptions import NoResultsFoundException
from ..permissions import Permission, permission_required

from . import main

@main.before_request
@login_required
def before_request():
    pass


@main.after_request
def turbolinks_location(response):
    response.headers["Turbolinks-Location"] = request.url
    return response


@main.route("/uploads/<filename>")
def uploaded_file(filename):
    send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@main.route("/")
def index():
    return render_template("main/base.html")
