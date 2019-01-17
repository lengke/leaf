import os


class BaseConfig():
    SECRET_KEY = os.getenv("SECRET_KEY", "seCRet/Keyyys238823u")


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

