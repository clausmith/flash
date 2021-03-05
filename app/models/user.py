import uuid
from datetime import datetime
from decimal import *
from enum import Enum

import pytz
from flask import url_for
from flask_login import AnonymousUserMixin, UserMixin
from money.currency import Currency
from money.money import Money
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, validates
from sqlalchemy.sql import expression
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager
from ..email import send_email
from ..enums import ApprovalStatus, Interval, IntervalCounts, Permission
from ..utils import generate_token, verify_token
from .helpers import UUID, IdMixin, TimezoneType, same_as


class User(UserMixin, IdMixin, db.Model):
    __tablename__ = "users"
    __prefix__ = "u"
    fname = db.Column(db.Text)
    lname = db.Column(db.Text)
    email = db.Column(db.Text, unique=True, index=True, nullable=False)
    password_hash = db.Column(db.Text)
    confirmed = db.Column(
        db.Boolean, default=False, server_default=expression.false(), nullable=False
    )
    confirmed_at = db.Column(db.DateTime(timezone=True))
    preregistered = db.Column(
        db.Boolean, default=False, server_default=expression.false(), nullable=False
    )
    confirmed_ip = db.Column(db.Text)
    last_seen = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))
    active = db.Column(db.Boolean, default=True, server_default=expression.true(), nullable=False)
    avatar_url = db.Column(db.Text)
    role_id = db.Column(UUID, db.ForeignKey("roles.id"))
    role = db.relationship("Role", foreign_keys=[role_id])

    current_timezone = db.Column(TimezoneType, default=same_as("default_timezone"))

    @hybrid_property
    def name(self):
        return f"{self.fname} {self.lname}"

    @name.expression
    def name(cls):
        return cls.fname + " " + cls.lname

    @validates("email")
    def validate_email(self, key, email):
        return email.lower()

    @hybrid_property
    def hash(self):
        return self.id.hex[:8]

    @hash.setter
    def hash(self, hash):
        raise AttributeError("Hash is a read-only attribute")

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return password and check_password_hash(self.password_hash, password)

    def generate_token(self, expiry=3600, **kwargs):
        return generate_token({"uuid": self.id.hex, **kwargs}, expiry)

    def verify_token(self, token):
        payload = verify_token(token)
        if not payload.get("uuid") == self.id.hex:
            return False
        return payload

    @classmethod
    def load_from_token(cls, token):
        payload = verify_token(token)
        if not payload.get("uuid"):
            return None
        return cls.query.get(payload["uuid"])

    @classmethod
    def reset_password(cls, token, new_password):
        user = cls.load_from_token(token)
        if not user:
            return None
        user.password = new_password
        return True

    def confirm(self, token, ip):
        if not self.verify_token(token):
            return False
        self.confirmed = True
        self.confirmed_at = datetime.now(pytz.utc)
        self.confirmed_ip = ip
        db.session.commit()
        return True

    def send_password_reset(self):
        token = self.generate_token()
        url = url_for("auth.password_reset", token=token, _external=True)
        send_email(
            self.email,
            "[Bureau] Password Reset Instructions",
            "email/password_reset",
            token_url=url,
            user=self,
        )

    def send_email_confirmation(self):
        token = self.generate_token()
        send_email(
            self.email,
            "Please confirm your account",
            "email/confirm",
            user=self,
            token_url=url_for("auth.confirm", token=token, _external=True),
        )

    def change_email(self, token, new_email):
        if not self.verify_token(token):
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.commit()
        return True

    def ping(self):
        self.last_seen = datetime.now(pytz.utc)
        db.session.commit()

    @staticmethod
    def preregister(email, send_welcome=True):
        u = User(email=email, preregister=True)
        db.session.add(u)
        db.session.commit()

    def __repr__(self):
        return "<User %r>" % self.email


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Both users and entities can have roles
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(UUID, default=uuid.uuid4, primary_key=True)
    name = db.Column(db.Text)
    default = db.Column(
        db.Boolean, default=False, server_default=expression.false(), nullable=False
    )
    description = db.Column(db.Text)
    permissions = db.Column(db.BigInteger, default=0)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def setup_roles():
        default_roles = [
            ("Admin", Permission.ADMIN, False),
            ("Employee", Permission.READ + Permission.EDIT, True),
        ]
        for name, perms, default in default_roles:
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name, permissions=perms, default=default)
                db.session.add(role)
        db.session.commit()
