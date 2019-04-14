import os


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig():
    SECRET_KEY = os.getenv("SECRET_KEY", "seCRet/Keyyys238823u")
    LEAP_MAIL_SUBJECT_PREFIX = "【LEAF通知】"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
    UPLOAD_PATH = os.path.join(basedir, 'uploads')

    MAIL_SERVER = "smtp.sendgrid.net"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "apikey"
    MAIL_PASSWORD = os.getenv("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = ("noreply@leaf.com")

    BOOTSTRAP_SERVE_LOCAL = True


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI_DEV")


class ProductionConfig(BaseConfig):
    pass


config_list = {
    "base": BaseConfig,
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

