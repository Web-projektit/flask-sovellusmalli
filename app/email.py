from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import sys

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            sys.stderr.write('Sahkoposti lahetetty\n')
        except Exception as ex:
            ex_name = ex.__class__.__name__
            sys.stderr.write('Sahkopostilahetysvirhe: ' + ex_name + '\n')
            sys.stderr.write(ex + '\n')

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['SP_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
