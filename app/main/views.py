from flask import abort, current_app, flash, g, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import func

from .. import db, models, tasks
from ..email import send_email
from ..enums import ApprovalStatus
from ..models import *
from . import main
from .forms import EditFlowForm, NewEmployeeForm


@main.before_request
@login_required
def before_request():
    pass


@main.route("/")
def index():
    return render_template("main/index.jinja")
