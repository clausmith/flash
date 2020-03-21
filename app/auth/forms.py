import wtforms as wtf

from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo, InputRequired, Length

from .. import db, models


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Length(0, 128)])
    password = wtf.PasswordField("Password", validators=[InputRequired()])
    remember_me = wtf.BooleanField("Remember Me?", default=False)


class SignUpForm(FlaskForm):
    company_name = wtf.StringField("Company Name")
    email = EmailField("Email", validators=[InputRequired(), Length(0, 128)])
    password = wtf.PasswordField("Password", validators=[InputRequired()])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        token = request.args.get("token")
        if token:
            user = models.User.load_from_token(token)
            if user:
                return True

        user = models.User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append(
                "An account for {} already exists.".format(user.email)
            )
            return False
        if not self.company_name.data:
            return False
        return True


class SetupForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    colour = StringField("Your favourite colour")
    avatar = FileField("Upload a profile photo")
