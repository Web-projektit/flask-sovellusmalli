# React-sovelluksen käynnistäminen Flask-sovelluksen Blueprintissä.
from flask import Blueprint, send_from_directory, request, make_response, jsonify
import os
# from ..reactapi.views import createResponse

# Huom. static_folder viittaa blueprint- eli tässä react-kansioon.
react = Blueprint('react', __name__,
                  url_prefix='/react-sovellusmalli',
                  static_folder='react-sovellusmalli',
                  template_folder='react-sovellusmalli'
                  )

def createResponse(message):
    # CORS:n vaatimat Headerit
    default_origin = 'http://localhost:3000'
    origin = request.headers.get('Origin',default_origin)
    response = make_response(message)
    response.headers.set('Access-Control-Allow-Credentials','true')
    response.headers.set('Access-Control-Allow-Origin',origin) 
    return response

@react.app_errorhandler(404)
def page_not_found(e):
    print('page_not_found:'+request.path)
    message = f'Virhe react-flask-blueprintissä: Kohdeosoitetta {request.path} ei löydy.'
    return createResponse(message)

'''
Huom. url_prefix, homepage ja basename ja niiden kauttaviivat             
Flask Blueprint url_prefix='/react-sovellusmalli',
React package.json: "homepage": "/react-sovellusmalli/"
React index.js: Router basename="/react-sovellusmalli"
React käyttää autentikointiin reactapi-blueprinttiä
'''
@react.route('/', defaults={'path': ''})
@react.route('/<path:path>')
def serve(path):
    print('serve:'+path)
    if path != "" and os.path.exists(react.static_folder + '/' + path):
        print(f'serve:polku {path} löytyi')
        return send_from_directory(react.static_folder, path)
    else:
        print('serve:index.html')
        return send_from_directory(react.static_folder, 'index.html')
