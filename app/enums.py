from enum import IntEnum

import pytz

from .utils import BaseEnum


class Permission(object):
    READ = 1
    EDIT = 2
    ADMIN = 16


Timezone = BaseEnum("Timezone", [(tz, tz) for tz in pytz.common_timezones])
