import hashlib
import pytz
import random

from app import db, models
from app.permissions import Permission

from click import progressbar
from datetime import datetime, timedelta
from faker import Faker
from slugify import slugify

fake = Faker()


class BootstrapException(Exception):
    pass


class Bootstrap(object):

    def setup_default_roles(self):
        default_roles = [("Administrator", Permission.ADMIN), ("Employee", 0)]
        for name, perms in default_roles:
            role = models.Role(name=name, permissions=perms)
            db.session.add(role)

    def __init__(self, initialize=False, recreate=False):
        if not initialize:
            return

        if recreate:
            db.drop_all()
            db.create_all()
