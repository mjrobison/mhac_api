import configparser
#import psycopg2
#from sqlalchemy.dialects.postgresql import UUID

# Read Config File
config = configparser.ConfigParser()
config.read('../db.conf')

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

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
