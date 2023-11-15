from flask import Flask
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from config import config
import logging
import os
import sys
from sqlalchemy.pool import QueuePool

logging.getLogger('flask_cors').level = logging.DEBUG
# Tulostukset Azuren virhekonsoliin via stderr
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)
# Tulostukset Azuren konsoliin via stdout
# stdout_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stdout_handler)

bootstrap = Bootstrap()
fa = FontAwesome()
mail = Mail()
moment = Moment()
if 'DYNO' in os.environ:
    # Lost connection to MySQL server during query (ClearDB)
    db = SQLAlchemy(engine_options={"pool_size": 10, "poolclass":QueuePool, "pool_pre_ping":True})
else:
    db = SQLAlchemy()

# if 'WEBSITE_HOSTNAME' not in os.environ:
    # Running in other environments, enable CSRF protection
    # csrf = CSRFProtect()

csrf = CSRFProtect()    

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
'''Jos blueprintille tarvitaan oma unauthorized_handler, se
voidaan toteuttaa aiheuttamalla puuttuvalla login_view:llä
401-virhe ja käsitellä se blueprintin 401-virhekäsittelijällä.'''
login_manager.blueprint_login_views = {'reactapi':'','react':''}
''' Jos taas yksi login_manager ja sen unauthorized_handler riittävät,
tämä ei aiheuta 401-virhettä:
login_manager.unauthorized_handler(kirjautumisvirhe)'''

def create_app(config_name):
    app = Flask(__name__)
    # Set the Flask app logger to use the created logger
    # app.logger.handlers = logger.handlers
    # app.logger.addHandler(logging.StreamHandler()) 
    '''
    CORS mm. Reactia varten, koko sovellukseen ml. Blueprintit
    Lisää headerit:
    1   Access-Control-Allow-Origin: Specifies the allowed origins that are allowed to access the resource. It can be set to "*" to allow all origins or specific origins.
    2   Access-Control-Allow-Methods: Specifies the allowed HTTP methods for the resource.
    3   Access-Control-Allow-Headers: Specifies the allowed headers in the actual request.
        Sisältää Content-Type
    4   Access-Control-Expose-Headers: Specifies the headers that can be exposed to the client.
        Access-Control-Allow-Credentials: Specifies whether the response can be exposed when the request's credentials mode is included.
        Ei sisälly automaattisesti
    '''
    CORS(app,supports_credentials=True,expose_headers=["Content-Type","X-CSRFToken"])
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # print(config[config_name].SQLALCHEMY_DATABASE_URI)
    bootstrap.init_app(app)
    fa.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    #if 'WEBSITE_HOSTNAME' not in os.environ:
    # Running in other environments, enable CSRF protection
    csrf.init_app(app) 

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .reactapi import reactapi as reactapi_blueprint
    # Tarvitaanko tätä, toimisiko?
    # CORS(reactapi_blueprint)
    app.register_blueprint(reactapi_blueprint, url_prefix='/reactapi')
 
    from .react import react as react_blueprint
    app.register_blueprint(react_blueprint)

    return app
