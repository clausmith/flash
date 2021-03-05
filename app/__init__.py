import logging
from datetime import datetime

import sentry_sdk
from celery import Celery
from chrononaut import VersionedSQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData

from config import config

from . import utils
from .extensions.webpack import Webpack
from .permissions import Permission

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

celery = Celery(__name__)
csrf = CSRFProtect()
db = VersionedSQLAlchemy(metadata=metadata)
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
login_manager.login_message_category = "primary"
mail = Mail()
migrate = Migrate(compare_type=True)
redis = FlaskRedis()
webpack = Webpack()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if not app.config["DEBUG"] and not app.config["TESTING"]:
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"], integrations=[CeleryIntegration(), FlaskIntegration()],
        )

    app.jinja_env.globals["is_hidden_field"] = utils.is_hidden_field_filter
    app.jinja_env.globals["url_for_related"] = utils.url_for_related
    app.jinja_env.filters["datetime"] = utils.format_datetime
    app.jinja_env.globals["utcnow"] = datetime.utcnow
    app.jinja_env.globals["now"] = lambda: datetime.now(app.config["APP_TIMEZONE"])
    app.jinja_env.globals["Permission"] = Permission
    app.jinja_env.globals["section"] = (
        lambda: request.path.strip("/").split("/")[0] if request.path.strip("/") else None
    )

    celery.conf.update(app.config)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    redis.init_app(app)
    webpack.init_app(app)

    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .api import api_module as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db, **{k: getattr(models, k) for k in models.__all__})

    @app.teardown_appcontext
    def remove_session(exception=None):
        db.session.remove()

    app.cli.add_command(seed)

    return app


@click.command("seed")
@click.option("--recreate", is_flag=True)
@with_appcontext
def seed(recreate):
    from data.bootstrap import Bootstrap

    if recreate:
        click.confirm("Are you SURE you want to drop the database?", abort=True)
    click.echo("Generating data")
    Bootstrap(True, recreate)
