from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .. import db, models
from ..email import send_email
from ..utils import generate_token, verify_token
from . import auth
from .forms import LoginForm, PasswordResetForm, PasswordResetRequestForm


@auth.before_app_request
def before_request():
    if not request.endpoint:
        abort(404)
    if current_user.is_authenticated:
        current_user.ping()
        if (
            not current_user.confirmed
            and request.blueprint != "auth"
            and request.endpoint != "static"
        ):
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.jinja")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    if current_user.confirmed:
        return redirect(url_for("main.index"))

    current_user.send_email_confirmation()
    flash("A new confirmation email has been sent")
    return redirect(url_for("auth.unconfirmed"))


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token, request.remote_addr):
        db.session.commit()
        flash("Your email has been confirmed")
    else:
        flash("The confirmation link is invalid or expired")
    return redirect(url_for("main.index"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid username or password", "primary")
    return render_template("auth/login.jinja", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("auth.login"))


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user:
            user.send_password_reset()
        flash(
            "An email has been sent with instructions on how to reset your password.", "primary",
        )
    return render_template("auth/password_reset_request.jinja", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        if models.User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password was changed successfully", "primary")
            return redirect(url_for("auth.login"))
        else:
            flash("The password reset URL is either invalid or expired", "error")
            return redirect(url_for("auth.login"))

    return render_template("auth/password_reset.jinja", form=form)
