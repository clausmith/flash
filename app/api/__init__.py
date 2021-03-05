from flask import Blueprint
from flask_restful import Api

from .. import db
from ..models import *

api_module = Blueprint("api", __name__)
api = Api(api_module)
