from functools import wraps
from flask import abort
from flask_login import current_user

"""
Permissions are the entries of a matrix of resources x capabilities
"""


class Permission:
    # Clients
    ADMIN = 2 ** 63 - 1


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
