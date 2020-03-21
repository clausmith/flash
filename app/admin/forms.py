import wtforms as wtf

from flask_wtf import FlaskForm

from .. import models
from ..models.agreement import plans
from ..utils import QuerySelectField