from flask import Flask
from leap.settings import config_list
from leap.blueprints.main import main
from leap.blueprints.auth import auth
from leap.ext import db, login_manager, mail, bootstrap, moment


def create_app(config_name=None):
    if config_name is None:
        current_config = config_list["development"]
    else:
        current_config = config_list[config_name]

    app = Flask("leap")
    app.config.from_object(current_config)
    register_exts(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")


def register_exts(app):
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)




