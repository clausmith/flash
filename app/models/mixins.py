import pytz
import uuid

from chrononaut import Versioned
from datetime import datetime
from flask_login import current_user
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from .. import db
from ..exceptions import NoResultsFoundException

__all__ = ["IdMixin", "UUID", "Versioned"]

UUID = UUID(as_uuid=True)


class IdMixin(object):
    id = db.Column(UUID, default=uuid.uuid4, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(pytz.utc)
    )
