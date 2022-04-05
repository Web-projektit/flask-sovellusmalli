import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flaskprojekti]'
    FLASKY_MAIL_SENDER = 'Flaskprojekti Admin <flaskprojekti@example.com>'
    FLASKY_ADMIN = os.environ.get('FP_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class LocalConfig(Config):
    DEBUG = True
    DB_USERNAME = os.environ.get('LOCAL_DB_USERNAME')
    DB_PASSWORD = os.environ.get('LOCAL_DB_PASSWORD')
    DB_NAME = os.environ.get('LOCAL_DB_NAME')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@localhost:3306/' + DB_NAME
    # SQLALCHEMY_ECHO = True (dokumentaatio)
    SQLALCHEMY_ECHO = "debug"
    # WTF_CSRF_ENABLED = False

class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL')
    SQLALCHEMY_ECHO = "debug"
    # WTF_CSRF_ENABLED = False    

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
