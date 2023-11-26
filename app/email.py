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
            sys.stderr.write(str(ex) + '\n')

def send_email(to, subject, template, pdf_stream=None, pdf_filename="document.pdf", **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FS_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FS_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # Attach PDF if stream is provided
    if pdf_stream:
        pdf_stream.seek(0)  # Rewind to beginning of the file
        msg.attach(pdf_filename, "application/pdf", pdf_stream.read())
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
