import uuid
from datetime import datetime

import pytz
import sqlalchemy.types as types
from flask import abort
from flask_login import current_user
from sqlalchemy.dialects.postgresql import UUID

from .. import db
from ..utils import b57_decode_uuid, b57_encode_uuid

UUID = UUID(as_uuid=True)


class TimezoneType(types.TypeDecorator):
    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return pytz.timezone(value)


def same_as(column_name, fallback=None):
    """Helper function for setting a column default the same as another live value at insert time.
    `fallback`, which can be None`, is needed so that if we don't have an inserted value we can
    still have a default, e.g., for Flask-Admin to dynamically populate a field.
    See: https://stackoverflow.com/questions/36579355/
                 sqlalchemy-set-default-value-of-one-column-to-that-of-another-column
    """

    def default_function(context):
        if context is None:
            return fallback
        return context.current_parameters.get(column_name)

    return default_function


class IdMixin:
    id = db.Column(UUID, default=uuid.uuid4, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.utc))

    @property
    def public_id(self):
        prefix = self.__class__.__name__.lower()
        if hasattr(self, "__prefix__"):
            prefix = self.__prefix__
        elif len(self.__class__.__name__) >= 3:
            prefix = prefix[:3]
        return f"{prefix}_{b57_encode_uuid(self.id)}"

    @classmethod
    def uget(cls, k):
        obj = cls.query.get(b57_decode_uuid(k.split("_")[1]))
        if not obj:
            return None
        if current_user and hasattr(obj, "user") and getattr(obj, "user") != current_user:
            raise
        return obj

    @classmethod
    def uget_or_abort(cls, k):
        try:
            obj = cls.uget(k)
            if not obj:
                abort(404)
        except:
            abort(403)

        return obj

    def __repr__(self):
        return rf"<{self.__class__.__name__} {self.public_id}>"
