from flask import Flask
from leaf.settings import config_list
from leaf.blueprints.main import main
from leaf.blueprints.auth import auth
from leaf.blueprints.admin import admin
from leaf.ext import db, login_manager, mail, bootstrap, moment
from leaf.utils import handle_file_size


def create_app(config_name=None):
    if config_name is None:
        current_config = config_list["development"]
    else:
        current_config = config_list[config_name]

    app = Flask("leaf")
    app.config.from_object(current_config)
    register_exts(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")


def register_exts(app):
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    app.add_template_filter(handle_file_size, 'size')



