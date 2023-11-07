from flask import render_template,jsonify,current_app
from werkzeug.exceptions import RequestEntityTooLarge
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(e):
    # You can return a custom response here
    app = current_app._get_current_object()
    koko = round(app.config['MAX_CONTENT_LENGTH'] / (1000 * 1000))
    errmsg = f"Kuvaa ei tallennettu, sen koko saa olla maks. {koko} MB."
    return jsonify(virhe=errmsg)
