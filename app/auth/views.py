import hashlib
import os
import pytz

from flask import (
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user, logout_user, login_required, current_user
from slackclient import SlackClient
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from . import auth
from .forms import LoginForm, SetupForm, SignUpForm
from .. import db, models
from ..email import send_email_template


@auth.before_app_request
def before_request():
    g.account = None
    if current_user.is_authenticated:
        g.account = current_user.account
        if g.account and g.account.settings.get("timezone"):
            g.tz = pytz.timezone(g.account.settings.get("timezone"))
        else:
            g.tz = current_app.config["APP_TIMEZONE"]

        current_user.ping()
        if (
            not current_user.confirmed
            and request.endpoint
            and request.blueprint != "auth"
            and request.endpoint != "static"
        ):
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_email_template(
        current_user.email,
        "Please confirm your account",
        "email/confirm",
        user=current_user,
        token_url=url_for("auth.confirm", token=token, _scheme="https", _external=True),
    )
    flash("A new confirmation email has been sent")
    return redirect(url_for("auth.unconfirmed"))


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token, request.remote_addr):
        flash("Your email has been confirmed")
        return redirect(url_for("main.index"))
    flash("The confirmation link is invalid or expired")
    return redirect(url_for("auth.unconfirmed"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data.lower()).first()
        if (
            user
            and user.active
            and user.password_hash
            and user.verify_password(form.password.data)
        ):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid username or password")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def registration():
    token = request.args.get("token")
    user = None
    preregistered = False
    if token:
        preregistered = True
        user = models.User.load_from_token(token)
        if not user:
            flash("The confirmation link is invalid or expired")
    form = SignUpForm(obj=user)
    if form.validate_on_submit():
        if not user:
            account = models.Account(name=form.company_name.data)
            db.session.add(account)
            admin_role = account.roles.filter_by(name="Administrator").first()
            user = models.User(account=account, role=admin_role)
            user.email = form.email.data.lower()
            db.session.add(user)
            token = current_user.generate_token()
            send_email_template(
                user.email,
                "Please confirm your account",
                "email/confirm",
                user=user,
                token_url=url_for("auth.confirm", token=token, _external=True),
            )
        else:  # We have a preregistration token
            user.confirm(token, request.remote_addr)
            user.active = True
        user.password = form.password.data
        db.session.commit()
        flash("Your account was created successfully.")
        login_user(user)
        return redirect(url_for("auth.unconfirmed"))
    else:
        current_app.logger.debug(form.errors)
    return render_template(
        "auth/registration.html", form=form, preregistered=preregistered
    )


@auth.route("/setup", methods=["GET", "POST"])
@login_required
def setup_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        f = form.avatar.data
        filename, ext = os.path.splitext(secure_filename(f.filename))
        filename = ".".join([secure_filename(f.read()).hexdigest(), ext])
        f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        current_user.avatar_url = url_for("main.uploaded_file", filename=filename)
