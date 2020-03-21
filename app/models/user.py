import hashlib
import pytz
import secrets

from datetime import datetime
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import BadSignature, TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import and_
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db, login_manager

from .mixins import IdMixin, UUID

USER_COLOURS = [
    "bg-blue",
    "bg-azure",
    "bg-indigo",
    "bg-purple",
    "bg-pink",
    "bg-red",
    "bg-orange",
    "bg-yellow",
    "bg-lime",
    "bg-green",
    "bg-teal",
    "bg-cyan",
]


class User(db.Model, IdMixin, UserMixin):
    __tablename__ = "users"
    __searchable__ = ["fname", "lname", "phone_number", "email"]
    __chrononaut_untracked__ = ["last_seen"]
    __chrononaut_hidden__ = ["password_hash"]
    email = db.Column(db.Text, unique=True, index=True)
    password_hash = db.Column(db.Text)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime(timezone=True))
    confirmed_ip = db.Column(db.Text)
    stripe_id = db.Column(db.Text, unique=True, index=True)
    last_seen = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(pytz.utc)
    )
    active = db.Column(db.Boolean, default=True)
    api_key = db.Column(db.Text, unique=True)
    avatar_url = db.Column(db.Text)
    colour = db.Column(db.Text)
    fname = db.Column(db.Text)
    lname = db.Column(db.Text)
    phone_number = db.Column(db.Text)
    role_id = db.Column(UUID, db.ForeignKey("roles.id"))
    role = db.relationship("Role")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if not self.api_key:
            self.api_key = secrets.token_urlsafe()

    def __repr__(self):
        return "<User {}>".format(self.email)

    @classmethod
    def preregister(cls, **kwargs):
        ip = ""
        if request.access_route:
            ip = request.access_route[0]
        else:
            ip = request.remote_addr
        user = cls(**kwargs)
        active = False
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def load_from_token(cls, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except BadSignature as e:
            return None
        return cls.query.get(data.get("uuid"))

    @hybrid_property
    def hash(self):
        return self.id.hex[:8]

    @property
    def colour(self):
        return USER_COLOURS[self.id.int % len(USER_COLOURS)]

    @hybrid_property
    def name(self):
        if not self.fname:
            return self.email
        return "{} {}".format(self.fname or "", self.lname or "")

    @name.expression
    def name(cls):
        return cls.fname + " " + cls.lname

    @property
    def initials(self):
        initials = ""
        if self.fname:
            initials += self.fname[0]
        if self.lname:
            initials += self.lname[0]
        return initials

    @hash.setter
    def hash(self, hash):
        raise AttributeError("Hash is a read-only attribute")

    @property
    def md5(self):
        m = hashlib.md5()
        m.update(self.email.encode("utf-8"))
        return m.hexdigest()

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"uuid": self.id.hex})

    def verify_token(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except BadSignature as e:
            return False
        if data.get("uuid") != self.id.hex:
            return False
        return True

    def confirm(self, token, ip):
        if not self.verify_token(token):
            return False
        self.confirmed = True
        self.confirmed_at = datetime.now(pytz.utc)
        self.confirmed_ip = ip
        db.session.commit()
        return True

    def reset_password(self, token, new_password):
        if not self.verify_token(token):
            return False
        self.password = new_password
        db.session.commit()
        return True

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

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
