import enum
import uuid

import wtforms as wtf
from flask import current_app, request
from flask_wtf import FlaskForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pytz import timezone

SUBMIT_METHODS = set(("POST", "PUT", "PATCH", "DELETE"))

ALPHA57 = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def MultiForm(FlaskForm):
    submit = wtf.SubmitField("Submit")

    def is_submitted(self):
        return bool(request) and (request.method in SUBMIT_METHODS) and self.submit.data


def pagination_headers(query, res, per_page, bp, **kwargs):
    links = []
    if query.has_next:
        next_url = bp.url_for(res, page=query.next_num, per_page=per_page, **kwargs)
        last_url = bp.url_for(res, page=query.pages, per_page=per_page, **kwargs)

        links.append('<{}>; rel="next"'.format(next_url))
        links.append('<{}>; rel="last"'.format(last_url))

    if query.page > 1:
        prev_url = bp.url_for(res, page=query.prev_num, per_page=per_page, **kwargs)
        first_url = bp.url_for(res, per_page=per_page, **kwargs)

        links.append('<{}>; rel="prev"'.format(prev_url))
        links.append('<{}>; rel="first"'.format(first_url))
    return ", ".join(links)


def is_hidden_field_filter(field):
    return field.type in ["HiddenField", "CSRFTokenField"]


def url_for_related(endpoint, remove_args=[], **kwargs):
    args = request.args.copy()
    for key in remove_args:
        args.pop(key, None)

    new_args = {}
    new_args.update(args)
    new_args.update(request.view_args)
    new_args.update(kwargs)
    return url_for(endpoint, **new_args)


def generate_token(payload, expiry=3600):
    s = Serializer(current_app.config["SECRET_KEY"], expiry)
    return s.dumps(payload)


def format_datetime(value, format="%B %-d, %Y"):
    if not value:
        return ""
    if isinstance(value, str):
        value = parser.parse(value)
    if not hasattr(value, "tzinfo"):
        return value.strftime(format)
    est = timezone("US/Eastern")
    utc = timezone("UTC")
    if not value.tzinfo:
        tz_aware_dt = utc.localize(value)
    else:
        tz_aware_dt = value
    local_dt = tz_aware_dt.astimezone(est)
    return local_dt.strftime(format)


def format_price(value, format="${:,.2f}"):
    return format.format(value / 100)


def verify_token(token):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        payload = s.loads(token)
    except BadSignature as e:
        return False
    return payload


def b57_encode_uuid(u, alpha=ALPHA57):
    output = ""
    n = u.int
    while n:
        n, r = divmod(n, len(alpha))
        output += alpha[r]
    return output[::-1]


def b57_decode_uuid(s, alpha=ALPHA57):
    n = 0
    for c in s:
        n = n * len(alpha) + alpha.index(c)
    return uuid.UUID(int=n)


class BaseEnum(str, enum.Enum):
    """
    Used for creating non-SQL-native Enum columns in SQLAlchemy models.
    This causes SQLAlchemy to use native db.Text columns but validate that the value is
    in the Enum of allowed values on create/update.
    If a value is not in the allowed values, SQLAlchemy will raise a
    sqlalchemy.exc.StatementError
    First, create an Enum class inheriting from this class:
    class ColorName(BaseEnum):
        Red = "red"
        Green = "green"
        Blue = "blue"
    You can then use this as a column type in a SQLALchemy model:
    color = db.Column(
        db.Enum(
            ColorName,
            validate_strings=True,
            native_enum=False,
            create_constraint=False,
        )
    )
    """

    @classmethod
    def has_value(cls, value: str):
        return value in cls.values()

    @classmethod
    def values(cls):
        return [e.value for e in cls]
