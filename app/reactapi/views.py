from flask import render_template, redirect, request, \
    url_for, flash, current_app, jsonify, make_response, \
    send_from_directory
from flask_login import (
    login_user,logout_user, 
    login_required, current_user )
from . import reactapi
from .. import db
from ..models import User
from ..email import send_email
from ..auth.forms import LoginForm, RegistrationForm, ProfileForm
from flask_cors import cross_origin
from flask_wtf.csrf import generate_csrf,CSRFError
import sys
from urllib.parse import urlencode

# By redirecting sys.stderr to sys.stdout, both error messages and print statements 
# will be sent to the standard output stream and captured in the log stream in Azure.
# sys.stderr = sys.stdout

def createResponse(message):
    # CORS:n vaatimat Headerit
    default_origin = 'http://localhost:3000'
    origin = request.headers.get('Origin',default_origin)
    response = make_response(jsonify(message))  
    # Määritetään CORS-alustuksessa
    # response.headers.set('Access-Control-Allow-Credentials','true')
    # Jos vaaditaan muuta kuin CORS-alustuksen '*'
    response.headers.set('Access-Control-Allow-Origin',origin) 
    return response


@reactapi.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    message = {'virhe':f'csrf-token puuttuu ({e.description}), headers:{str(request.headers)}'}
    # print(f"\nPRINT:reactapi CSFRError,SIGNIN headers:{str(request.headers)}\n")
    sys.stderr.write(f"\nreactapi CSFRError,headers:{str(request.headers)}\n")
    return createResponse(message)


@reactapi.app_errorhandler(401)
def page_not_allowed(e):
    app = current_app._get_current_object()
    app.logger.debug('reactapi.app_errorhandler 401,endpoint %s', request.endpoint)
    app.logger.debug('reactapi.app_errorhandler 401,path %s', request.path)
    if request.endpoint == 'reactapi.confirm':
        # Vrt. vastaava Flask route:
        # login_url = url_for('login', confirm_token=confirm_token, _external=True)
        redirect_url = app.config['REACT_LOGIN'] + "?next=" + request.path
        return redirect(redirect_url)
    message = {'virhe':'Pääsy epäonnistui.'}
    return createResponse(message)


@reactapi.app_errorhandler(404)
def page_not_found(e):
    message = {'virhe':'Kohdeosoitetta ei löydy.'}
    return createResponse(message)

'''
@reactapi.before_request
def normalize_csrf_header():
    csrf_header = request.headers.get('X-Csrftoken')
    if csrf_header is not None:
        # Huom. request.headersiä ei voi muuttaa suoraan:
        # request.headers['X-CSRFToken'] = csrf_header
        request.environ['HTTP_X_CSRFTOKEN'] = csrf_header
'''        

@reactapi.before_request
    # Huom. 
    # before_app_request: for all application requests
    # before_request: applies only to requests that belong to the blueprint
    #
def before_request():
    if current_user.is_authenticated:
        # Tallennetaan last_seen
        current_user.ping()
        app = current_app._get_current_object()
        app.logger.debug('reactapi.before_request,endpoint %s', request.endpoint)
        app.logger.debug('reactapi.before_request,blueprint %s', request.blueprint)
        if not current_user.confirmed \
            and request.endpoint \
            and request.endpoint != 'static':
            # and not request.path.startswith('/static/'):
            # Huom. is_authenticated: kirjautunut
            # Kirjautuneet vahvistamattomat käyttäjät ohjataan muualta paitsi
            # reactapi-blueprintista unconfirmed.html-sivulle
            app.logger.debug('reactapi.before_request,path %s', request.path)
            # return redirect(url_for('reactapi.unconfirmed'))


# Reactin käynnistäminen Flaskistä
# Serve the React app's index.html file
'''@reactapi.route('/')
def serve_index():
    return send_from_directory(react_polku, path)

# Serve all the static files required by the React app
@reactapi.route(react_static+'/<path:path>')
def serve_static(path):
    return send_from_directory(react_static, path)
'''

from flask import Flask

app = Flask(__name__)

'''
@app.route('/', methods=['OPTIONS'])
def handle_preflight():
    response = jsonify({})
    response.headers['Content-Type'] = 'multipart/form-data'  # Set the Content-Type header
    response.headers['Access-Control-Allow-Origin'] = '*'  # Set the appropriate CORS headers
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
    return response
'''


@reactapi.route("/getcsrf", methods=["GET"])
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
def get_csrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    # Määritetään CORS-alustuksessa
    # response.headers.set('Access-Control-Expose-Headers','X-CSRFToken') 
    response.headers.set("X-CSRFToken", token)
    return response


# Huom. Tässä on jäetty 'OPTIONS' ja origins varmuuden vuoksi,
# axios-kutsuja ei ole testattu ilman niitä,
# fetch-kutsut toimivat ilmankin.
# Axios on korvattu fetchillä, jotta käyttäjän istunto säilyy eli
# sen vaatimat evästeet välittyvät selaimelta oikein. 
@reactapi.route('/logout')
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
# Huom. Header asettuu automaattisesti oikein: 
# Access-Control-Allow-Origin: http://localhost:3000
@login_required
def logout():
    # sessio = request.cookies.get('session')
    # print(f"reactapi/logout,sessio:{sessio}")
    logout_user()
    return "OK"


@reactapi.route('/signin', methods=['GET','POST'])
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
def signin():
    # print(f"\nPRINT:reactapi,views.py,SIGNIN headers:{str(request.headers)}\n")
    # sys.stderr.write(f"\nWRITE:reactapi,views.py,SIGNIN headers:{str(request.headers)}\n")
    form = LoginForm()
    sys.stderr.write(f"\nreactapi,views.py,SIGNIN data:{form.email.data}\n")
    if form.validate_on_submit():
        sys.stderr.write(f"\nreactapi, views.py,SIGNIN, validate_on_submit OK\n")
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # next = request.args.get('next')
            # if next is None or not next.startswith('/'):
            #    next = url_for('main.index')
            sys.stderr.write(f"\nviews.py,SIGNIN, request.args:{request.args}\n")
            next = request.args.get('next')
            sys.stderr.write(f"\nviews.py,SIGNIN:OK, next:{next}, confirmed:{user.confirmed}\n")
            if next is None or not next.startswith('/'):
                # next = url_for('main.index')
                if user.confirmed:
                    return jsonify({'ok':'OK','confirmed':'1'})
                else:
                    return jsonify({'ok':'OK'})
            return redirect(next)
        else:
            response = jsonify({'virhe':'Väärät tunnukset'})
            # response.status_code = 200
            return response 
    else:
        # print("validointivirheet:"+str(form.errors))
        response = jsonify(form.errors)
        # response.status_code = 200
        return response
    

@reactapi.route('/signup', methods=['GET', 'POST'])
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
def signup():
    form = RegistrationForm()
    sys.stderr.write('\nviews.py,SIGNUP,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'reactapi/email/confirm', user=user, token=token)
        # Huom. ilmoitus sähköpostivahvistuksesta tarvitaan käyttöliittymään
        # flash('A confirmation email has been sent to you by email.')
        return "OK"
    else:
        # print("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify(form.errors)
        response.status_code = 200
        return response


@reactapi.route('/unconfirmed')
def unconfirmed():
    app = current_app._get_current_object()
    app.logger.debug('reactapi.unconfirmed,endnode: %s',request.endpoint)
    if current_user.is_anonymous or current_user.confirmed:
        app.logger.debug('reactapi.unconfirmed,redirect: %s',current_user.is_anonymous)
        return redirect(app.config['REACT_ORIGIN'])
    return redirect(app.config['REACT_UNCONFIRMED'])


@reactapi.route('/confirm/<token>')
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
@login_required
# Huom. login_required vie login-sivulle, ja kirjautuminen takaisin tänne
def confirm(token):
    app = current_app._get_current_object()
    app.logger.debug('/confirm,confirmed: %s',current_user.confirmed)
    app.logger.debug('/confirm,headers:' + str(request.headers))
    if current_user.confirmed:
        # Huom. Tähän vain sähköpostilinkistä kirjautuneena.
        # Siirtyminen uuteen ikkunaan ei-kirjautuneena
        # Huom. Nyt sama ilmoitus kuin ensi kertaa vahvistuksessa.
        app.logger.debug('/confirm,REACT_CONFIRMED:' + app.config['REACT_CONFIRMED'])
        return redirect(app.config['REACT_CONFIRMED'] + '?jo=jo')
        # message = "Sähköpostiosoite on jo vahvistettu."
        # return jsonify({'ok':"Virhe",'message':message})
    if current_user.confirm(token):
        app.logger.debug('/confirm,confirmed here')
        db.session.commit()
        message = "Sähköpostiosoite on vahvistettu."
        # redirect_url = f"{app.config['REACT_ORIGIN']}?message={message}"
        # return redirect(redirect_url)
        if request.headers.get('Referer'):
            # Kirjautumisen kautta
            return jsonify({'ok':"OK",'message':message})
        else:
            # Sähköpostilinkin kautta suoraan
            app.logger.debug('\n/confirm,REACT_CONFIRMED:' + app.config['REACT_CONFIRMED']+'\n')
            return redirect(app.config['REACT_CONFIRMED'])
    else:
        # Huom. Kun on jo kirjauduttu toisella välilehdellä, Referer-headeriä ei ole.
        # Suojattu reitti /unfirmed Reactissa johtaa sinne kirjautumisen kautta. 
        message = 'Vahvistuslinkki on virheellinen tai se ei ole enää voimassa.'
        # redirect_url = f"{app.config['REACT_UNCONFIRMED']}?message={message}"
        # return redirect(redirect_url)
        # return jsonify({'ok':"Virhe",'message':message})
        query_params = { 'message':message }
        encoded_params = urlencode(query_params)
        if request.headers.get('Referer'):
            # Kirjautumisen kautta
            return jsonify({'ok':"Virhe",'message':message})
        return redirect(app.config['REACT_UNCONFIRMED'] + "?" + encoded_params) 
    # return redirect(app.config['REACT_ORIGIN'])


@reactapi.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    app = current_app._get_current_object()
    app.logger.debug('/confirm: %s',current_user.email)
    send_email(current_user.email, 'Confirm Your Account',
               'reactapi/email/confirm', user=current_user, token=token)
    message = 'A new confirmation email has been sent to you by email.'
    return jsonify({'ok':"OK",'message':message})


@reactapi.route('/haeProfiili', methods=['GET', 'POST'])
# Tarvitaanko tätä, unsafe cross domain request?
# credentials:'include' => unsafe request => origin määritettävä muuksi kuin '*'
# @cross_origin(supports_credentials=True,origin='localhost:3000'
# Evästeet lähetetään myös cross domain
# @cross_origin(supports_credentials=True,origins=['http://localhost:3000'])
@cross_origin(supports_credentials=True)
@login_required
# Huom. Header Access-Control-Allow-Credentials: true ei välity,
# jos ei ole kirjautunut eli session-evästettä ei saavu, ja syntyy
# CORS-virhe. Näin myös, jos @login_manager.login_view on asettamatta, sillä tällöin 
# suoritus päättyy 401-virheeseen. Tämä tilanne käsitellään tässä
# Blueprintin 401-virhekäsittelijällä.  
def haeProfiili():
    id = current_user.get_id()
    # taulun rivi objektiksi
    print("RESPONSE:",current_user.get_id())
    user = {
        'email':current_user.email,
        'username':current_user.username
        }
    response = jsonify(user)
    response.status_code = 200
    return response


@reactapi.route('/tallennaProfiili', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def tallennaProfiili():
    form = ProfileForm()
    sys.stderr.write('\nviews.py,tallennaProfiili,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = current_user
        print('\n'\
            "user.email:",user.email,'\n'\
            "current_user.email:",current_user.email,'\n'\
            "form.email.data.lower():",form.email.data.lower(),'\n')
        '''
        Huom. 
        user-objektin muutokset näkyvät myös current_user-objektissa
        db.session.add(user)-komentoa ei tarvita
        vrt. 
        form.populate_obj(user) tai form.populate_obj(current_user)
        form = ProfileForm(obj=user)
        '''
        if current_user.email != form.email.data.lower():
            print("tallennaProfiili, uusi sähköpostiosoite")
            user.confirmed = False
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        # Huom. 
        # user.username = form.username.data
        # db.session.commit()   
        # toimisi myös 
        # Huom. Tässä muuttuu myös current_user
        form.populate_obj(user)
        print('\n'\
            "user.email:",user.email,'\n'\
            "current_user.email:",current_user.email,'\n'\
            "form.email.data.lower():",form.email.data.lower(),'\n')
        db.session.commit()   
        # flash('A confirmation email has been sent to you by email.')
        return "OK"
    else:
        # print("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify(form.errors)
        response.status_code = 200
        return response

'''
# Handle all other routes by serving the React app's index.html file
@reactapi.route('/<path:path>')
def serve_other_routes(path):
    return send_from_directory(react_polku, 'index.html')
'''