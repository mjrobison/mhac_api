import configparser
from configparser import SafeConfigParser
import os
# basedir = os.path.abspath(os.pardir)
basedir = os.getcwd()
print(basedir)
# Read Config File
filename = f'{basedir}/db.conf'
if os.path.isfile(filename):
    config = SafeConfigParser()
    config.read(filename)

print(filename)
config = configparser.ConfigParser()
config.read(filename)


db_user = config['DB']['user']
db_pass = config['DB']['password']
db_host = config['DB']['host']
db_port = config['DB']['port']
db_name = config['DB']['db']

class Config(object):
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(user=db_user,pw=db_pass,url=db_host,db=db_name,port=db_port)
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'This_IS_JUST_a_TEST'
    SQLALCHEMY_DATABASE_URI = DB_URL
    BRYPT_LOG_ROUNDS=15

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


from pydantic import BaseModel
from logging.handlers import RotatingFileHandler

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "mhac_api"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "mhac_api": {"handlers": ["default"], "level": LOG_LEVEL},
    }

config = {
    'production': ProductionConfig,
    'staging': StagingConfig,
    'development': DevelopmentConfig
}
