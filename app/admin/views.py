from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .. import db, models
from . import admin


@admin.route("/")
@login_required
def index():
    return render_template("admin/index.jinja")
