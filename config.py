import os
import pytz
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    APP_CONFIG = os.environ.get("APP_CONFIG")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    STRIPE_PUB_KEY = os.environ.get("STRIPE_PUB_KEY")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

    APP_ADMIN = os.environ.get("APP_ADMIN", "support@plinth.io")
    APP_MAIL_SUBJECT_PREFIX = os.environ.get("APP_MAIL_SUBJECT_PREFIX")
    APP_MAIL_SENDER = os.environ.get("APP_MAIL_SENDER", "Plinth <support@plinth.io>")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgres://db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT", 1025)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", False) == "True"

    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    APP_TIMEZONE = pytz.timezone(os.environ.get("APP_TIMEZONE", "US/Eastern"))

    BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )

    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")

    UPLOADS_DEFAULT_DEST = os.environ.get("UPLOADS_DEFAULT_DEST", "uploads")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", True)
    DEBUG = True


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME")

    @staticmethod
    def init_app(app):
        from werkzeug.contrib.fixers import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
