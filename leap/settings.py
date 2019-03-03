import os


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig():
    SECRET_KEY = os.getenv("SECRET_KEY", "seCRet/Keyyys238823u")
    LEAP_MAIL_SUBJECT_PREFIX = "【LEAP通知】"

    LEAP_ADMIN_EMAIL = "20167591@qq.com"

    CKEDITOR_SERVE_LOCAL = True
    MAIL_SERVER = "smtp.qq.com"
    MAIL_SUPPRESS_SEND = False
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = "20167591@qq.com"
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("20167591@qq.com")

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

