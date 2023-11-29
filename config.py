import os
import sys
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    '''
    Ympäristökohtaiset konfiguraatiot periytetään tästä.
    Konfiguraatioissa määritetään erityisesti 
    - tietokanta-asetukset
    - kuvien sijainti
    - Flaskin debug-tila
    - Virhelokien taso, esim. INFO, DEBUG, WARNING, ERROR
    - CORS ja CSRF
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vaikeasti arvattava salasana'
    MAIL_SERVER = os.environ.get('MAILTRAP_MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.environ.get('MAILTRAP_MAIL_PORT', '2525'))
    MAIL_USE_TLS = os.environ.get('MAILTRAP_MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAILTRAP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAILTRAP_MAIL_PASSWORD')
    FS_MAIL_SUBJECT_PREFIX = '[Flaskprojekti]'
    FS_MAIL_SENDER = 'Flaskprojekti Admin <flaskprojekti@example.com>'
    FS_ADMIN = os.environ.get('FS_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Kaikki SQL-kyselyt parametreineen ja tuloksineen tulostetaan konsoliin
    SQLALCHEMY_ECHO = "debug"
    CORS_HEADERS = 'Content-Type'
    FS_POSTS_PER_PAGE = 25
    KUVAPALVELU = 'local'
    # KUVAPOLKU = os.path.join(os.path.abspath('.'),'profiilikuvat/')
    KUVAPOLKU = os.path.join(os.path.dirname(__file__),'profiilikuvat/')
  
    MAX_CONTENT_LENGTH = 2 * 1000 * 1000
    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    @staticmethod
    def init_app(app):
        if app.config['KUVAPALVELU'] == 'local':
            kuvapolku = app.config['KUVAPOLKU']
            if not os.path.exists(kuvapolku):
                os.makedirs(kuvapolku)
        elif app.config['KUVAPALVELU'] == 'AzureHome':
            kuvapolku = app.config['KUVAPOLKU']
            msg_logger = f'The home directory is: {kuvapolku}.\n'
            # msg_stderr = f'Kotiosoite on: {kuvapolku}.\n'
            # msg_print = f'Kotiosoitteen tulostus on: {kuvapolku}.\n'
            # Tulostuu Azuren virhekonsoliin:
            app.logger.info(msg_logger)
            # Tulostuu Azuren virhekonsoliin:
            # sys.stderr.write(msg_stderr)
            # Ei tulostu Azuren virhekonsoliin:
            # print(msg_print)
            if not os.path.exists(kuvapolku):
                try:
                    os.makedirs(kuvapolku)
                except PermissionError:
                    errmsg = f'Permission denied: Unable to create directory {kuvapolku}.'
                    sys.stderr.write(errmsg + '\n')
                    app.logger.exception(errmsg)
                    app.logger.info(PermissionError)
        # pass

class LocalConfig(Config):
    DEBUG = True
    DB_USERNAME = os.environ.get('LOCAL_DB_USERNAME') or 'root'
    DB_PASSWORD = os.environ.get('LOCAL_DB_PASSWORD') or ''
    DB_NAME = os.environ.get('LOCAL_DB_NAME') or 'flask_sovellusmalli'
    DB_SERVER = os.environ.get('LOCAL_DB_SERVER') or 'localhost'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + ':3306/' + DB_NAME
    # Kaikki SQL-kyselyt tulostetaan konsoliin, vrt. SQLALCHEMY_ECHO = "debug"
    # SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = True
    REACT_ORIGIN = 'http://localhost:3000/react-sovellusmalli/'
    # REACT_ORIGIN = '/react-sovellusmalli/'
    REACT_LOGIN = REACT_ORIGIN + 'login'
    REACT_UNCONFIRMED = REACT_ORIGIN + 'unconfirmed'
    REACT_CONFIRMED = REACT_ORIGIN + 'confirmed'

class LocalDockerConfig(LocalConfig):
    DB_USERNAME = LocalConfig.DB_USERNAME
    DB_PASSWORD = LocalConfig.DB_PASSWORD
    DB_NAME = LocalConfig.DB_NAME
    DB_SERVER = os.environ.get('LOCAL_DOCKER_DB_SERVER') or 'host.docker.internal'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + ':3306/' + DB_NAME

class DevelopmentConfig(LocalConfig):
    KUVAPALVELU = 'S3'
    KUVAPOLKU = os.environ.get('S3_DOMAIN')

class XamppConfig(LocalConfig):
    REACT_ORIGIN = 'http://localhost/react-sovellusmalli/'
    REACT_LOGIN = REACT_ORIGIN + 'login'
    REACT_UNCONFIRMED = REACT_ORIGIN + 'unconfirmed'
    REACT_CONFIRMED = REACT_ORIGIN + 'confirmed'
    
class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CLEARDB_DATABASE_URL')
    MAIL_SERVER = os.environ.get('SENDGRID_MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('SENDGRID_MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('SENDGRID_MAIL_USE_TLS', 'true')
    # MAIL_USE_SSL = os.environ.get('MAILTRAP_MAIL_USE_SSL', 'false')   
    MAIL_USERNAME = os.environ.get('SENDGRID_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_MAIL_PASSWORD')
    FS_MAIL_SENDER = 'wohjelmointi@gmail.com'
    # WTF_CSRF_ENABLED = False    
    KUVAPALVELU = 'S3'
    KUVAPOLKU = os.environ.get('S3_DOMAIN')

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
    DB_SERVER = os.environ.get('AZURE_DB_SERVER') or 'localhost:3306'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + '/' + DB_NAME
    # print("SQLALCHEMY_DATABASE_URI Azure-palvelimelle " + DB_SERVER)
    # Huom. kuvien oletussijainti oli AWS S3, tässä se on Azure Blob Storage
    KUVAPALVELU = 'Azure'
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING') or 'DefaultEndpointsProtocol=https;AccountName=flasksovellusmalli;AccountKey=;EndpointSuffix=core.windows.net'
    AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER') or 'kuvat'
    WTF_CSRF_ENABLED = True
    # WTF_CSRF_HEADERS= ['X-Csrftoken']
    # WTF_CSRF_SSL_STRICT = True
    # WTF_CSRF_TIME_LIMIT = None
    # REACT_ORIGIN = '/react-sovellusmalli/'
    REACT_ORIGIN = os.environ.get('REACT_ORIGIN') or '/react-sovellusmalli/'
    REACT_LOGIN = REACT_ORIGIN + 'login'
    REACT_UNCONFIRMED = REACT_ORIGIN + 'unconfirmed'
    REACT_CONFIRMED = REACT_ORIGIN + 'confirmed'
    # Näiden tarpeellisuus tulisi testata, huom. WEBSITE_HOSTNAME on Azuressa valmiina
    CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('WEBSITE_HOSTNAME')] 
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'

'''class AzureOmniaConfig(AzureConfig):
    # Huom. Azuressa ympäristömuuttujien nimet ovat samat kuin Azure Omnia -palvelimella,
    # mutta niiden arvot ovat erilaiset, ja tämä konfiguraatio on tarpeeton.
    DB_USERNAME = os.environ.get('AZURE_OMNIA_DB_USERNAME') or 'root'
    DB_PASSWORD = os.environ.get('AZURE_OMNIA_DB_PASSWORD') or ''
    DB_NAME = os.environ.get('AZURE_OMNIA_DB_NAME') or 'flask_sovellusmalli'
    DB_SERVER = os.environ.get('AZURE_OMNIA_DB_SERVER') or 'localhost:3306'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + '/' + DB_NAME
'''
class AzureOmniaHomeConfig(AzureConfig):
    # Huom. kuvien oletussijainti oli Azure Blob Storage, 
    # tässä se on /home/profiilikuvat, voisi olla myös julkisesti saatavilla oleva URL 
    # /home/site/wwwroot/profiilikuvat
    # home = os.environ.get('HOME') or '/home'
    home = '/home'
    KUVAPALVELU = 'AzureHome'
    KUVAPOLKU = os.path.join(home, 'profiilikuvat/')
 
class AzureStaticConfig(AzureConfig):
    REACT_ORIGIN = os.environ.get('REACT_ORIGIN_STATIC') or '/react-sovellusmalli/'
    REACT_LOGIN = REACT_ORIGIN + 'login'
    REACT_UNCONFIRMED = REACT_ORIGIN + 'unconfirmed'
    REACT_CONFIRMED = REACT_ORIGIN + 'confirmed'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'localdocker': LocalDockerConfig,
    'xampp': XamppConfig,
    'heroku': HerokuConfig,
    'azure': AzureConfig,
    # 'azureomnia': AzureOmniaConfig,
    'azureomniahome': AzureOmniaHomeConfig,
    'azurestatic': AzureStaticConfig,
    'default': LocalConfig
}
