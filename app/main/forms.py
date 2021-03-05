import wtforms as wtf
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, HiddenField, PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length

from app import models
