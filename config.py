import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAILTRAP_MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAILTRAP_MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAILTRAP_MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAILTRAP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAILTRAP_MAIL_PASSWORD')
    FS_MAIL_SUBJECT_PREFIX = '[Flaskprojekti]'
    FS_MAIL_SENDER = 'Flaskprojekti Admin <flaskprojekti@example.com>'
    FS_ADMIN = os.environ.get('FS_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    FS_POSTS_PER_PAGE = 25
    KUVAPALVELU = 'S3'
    KUVAPOLKU = os.environ.get('S3_DOMAIN')
    MAX_CONTENT_LENGTH = 1 * 1000 * 1000

    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    @staticmethod
    def init_app(app):
        pass


class LocalConfig(Config):
    DEBUG = True
    DB_USERNAME = os.environ.get('LOCAL_DB_USERNAME') or 'root'
    DB_PASSWORD = os.environ.get('LOCAL_DB_PASSWORD') or ''
    DB_NAME = os.environ.get('LOCAL_DB_NAME') or 'flask_sovellusmalli'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@localhost:3306/' + DB_NAME
    # SQLALCHEMY_ECHO = True (dokumentaatio)
    SQLALCHEMY_ECHO = "debug"
    WTF_CSRF_ENABLED = True
    KUVAPALVELU = 'local'
    KUVAPOLKU = 'app/profiilikuvat/'

class DevelopmentConfig(LocalConfig):
    KUVAPALVELU = 'S3'
    KUVAPOLKU = os.environ.get('S3_DOMAIN')
    
class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL')
    SQLALCHEMY_ECHO = "debug"
    MAIL_SERVER = os.environ.get('SENDGRID_MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('SENDGRID_MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('SENDGRID_MAIL_USE_TLS', 'true')
    # MAIL_USE_SSL = os.environ.get('MAILTRAP_MAIL_USE_SSL', 'false')   
    MAIL_USERNAME = os.environ.get('SENDGRID_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_MAIL_PASSWORD')
    FS_MAIL_SENDER = 'wohjelmointi@gmail.com'
    # WTF_CSRF_ENABLED = False    

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    
class AzureConfig(Config):
    # pip install python-dotenv
    # pip install pymysql
    # from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
    # luo uusi MySQL-tietokanta, esim. phpMyAdmin
    # tallenna migrations-kansio uudella nimellä
    # poista tarvittaessa vanha alembic-taulu
    # uusi migraatioprosessi: flask db init, flask db migrate, flask db upgrade
    DB_USERNAME = os.environ.get('AZURE_DB_USERNAME') or 'root'
    DB_PASSWORD = os.environ.get('AZURE_DB_PASSWORD') or ''
    DB_NAME = os.environ.get('AZURE_DB_NAME') or 'flask_sovellusmalli'
    DB_SERVER = os.environ.get('AZURE_DB_SERVER') or 'localhost'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + ':3306/' + DB_NAME
    # print("SQLALCHEMY_DATABASE_URI Azure-palvelimelle " + DB_SERVER)
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_ECHO = "debug"

    CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('WEBSITE_HOSTNAME')] 
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'heroku': HerokuConfig,
    'azure': AzureConfig,
    'default': DevelopmentConfig
}
