from flask import Blueprint
from .. import db, models, tasks

main = Blueprint("main", __name__)

from . import views
