import logging
import sentry_sdk

from chrononaut import VersionedSQLAlchemy
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from config import config
from logging import Formatter
from logging.handlers import SysLogHandler
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration

from . import utils
from .extensions.webpack import Webpack
from .permissions import Permission

celery = Celery(__name__)
csrf = CSRFProtect()
db = VersionedSQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
login_manager.login_message_category = "primary"
mail = Mail()
redis = FlaskRedis()
webpack = Webpack()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if not app.config["DEBUG"] and not app.config["TESTING"]:
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[CeleryIntegration(), FlaskIntegration()],
        )

    handler = SysLogHandler()
    handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    app.jinja_env.globals["is_hidden_field"] = utils.is_hidden_field_filter
    app.jinja_env.globals["url_for_related"] = utils.url_for_related
    app.jinja_env.filters["datetime"] = utils.format_datetime
    app.jinja_env.globals["utcnow"] = datetime.utcnow
    app.jinja_env.globals["now"] = lambda: datetime.now(app.config["APP_TIMEZONE"])
    app.jinja_env.globals["Permission"] = Permission

    celery.conf.update(app.config)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    redis.init_app(app)
    webpack.init_app(app)

    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db, **{k: getattr(models, k) for k in models.__all__})

    app.cli.add_command(seed)

    @app.teardown_appcontext
    def remove_session(exception=None):
        db.session.remove()

    return app


@click.command("seed")
@with_appcontext
def seed():
    from data.bootstrap import Bootstrap

    Bootstrap(True, True)
