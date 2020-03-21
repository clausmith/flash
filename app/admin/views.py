from flask import redirect, render_template, request, url_for
from flask_login import login_required

from . import admin
from .. import db, models


@admin.route("/")
@login_required
def index():
    return render_template("admin/base.html")