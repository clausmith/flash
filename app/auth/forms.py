import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo, InputRequired, Length

from .. import db, models


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Length(0, 128)])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember Me?", default=False)


class PasswordResetRequestForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Length(0, 128)])


class PasswordResetForm(FlaskForm):
    password = PasswordField("New Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm New Password", validators=[InputRequired(), EqualTo("password")]
    )
