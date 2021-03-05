import os

import pytz
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    STRIPE_PUB_KEY = os.environ.get("STRIPE_PUB_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

    APP_ADMIN = os.environ.get("APP_ADMIN", "support@plinth.io")
    APP_MAIL_SUBJECT_PREFIX = os.environ.get("APP_MAIL_SUBJECT_PREFIX")
    APP_MAIL_SENDER = os.environ.get("APP_MAIL_SENDER", "App <app@plinth.io>")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgres://db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = os.environ.get("MAIL_PORT", 1025)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", False) == "True"

    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    APP_TIMEZONE = pytz.timezone(os.environ.get("APP_TIMEZONE", "US/Eastern"))

    BROKER_URL = os.environ.get("BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    REQUEST_BIN_URL = os.environ.get("REQUEST_BIN_URL", "http://requestbin:8000")
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", False)
    KONCH_SHELL = "ipy"
    KONCH_IPY_AUTORELOAD = True
    DEBUG = True

    def __init__(*args, **kwargs):
        super(DevelopmentConfig, self).__init__(*args, **kwargs)
        r = request.post(self.REQUEST_BIN_URL + "/bins")
        r.raise_for_status()
        bin_name = r.json().get("name")
        self.RACKSPACE_BASE_URL = self.REQUEST_BIN_URL


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgres:///plinth_test"
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    RACKSPACE_BASE_URL = os.environ.get("RACKSPACE_BASE_URL")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
