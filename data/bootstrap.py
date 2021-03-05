import hashlib
import random
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta
from faker import Faker
from flask_migrate import upgrade
from money.currency import Currency
from money.money import Money
from slugify import slugify

from app import db
from app.enums import *
from app.models import *

fake = Faker()

DEFAULT_EXCHANGE_RATES = [
    ("USD", "EUR", "0.8391430064"),
    ("USD", "GBP", "0.7467339629"),
    ("USD", "CAD", "1.3064824836"),
]


class BootstrapException(Exception):
    pass


class Bootstrap(object):
    @staticmethod
    def setup_default_user(email="admin@plinth.io", password="password"):
        # Add admin org

        user = User(
            email=email,
            password=password,
            fname="Test",
            lname="User",
            confirmed=True,
            confirmed_at=datetime.now(pytz.utc),
            confirmed_ip="127.0.0.1",
            setup_complete=True,
            avatar_url=fake.image_url(),
            default_timezone=pytz.timezone("Canada/Eastern"),
        )

        user.entity = Entity(
            name="Bureau Ventures Inc.",
            billing_rate=3500,
            default_description="Professional Services",
        )

        db.session.add(user)
        db.session.commit()

        return user

    def __init__(self, initialize=False, recreate=False):
        if not initialize:
            return

        if recreate:
            db.session.remove()
            db.drop_all()
            upgrade()
            db.create_all()

        u = User.query.filter_by(email="admin@plinth.io").first()
        if not u:
            u = self.setup_default_user()

        org = Organization(name="Test Company", domain=fake.domain_name())

        u.organization = org
