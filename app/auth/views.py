from flask import current_app, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm,\
    patterns


# Huom. Tässä myöskin reactapi-kutsut on otettu huomioon
@auth.before_app_request
    # Huom. 
    # before_app_request: for all application requests
    # before_request: applies only to requests that belong to the blueprint
    #
def before_app_request():
    if current_user.is_authenticated:
        # Kirjautunut, tallennetaan last_seen
        current_user.ping()
        app = current_app._get_current_object()
        app.logger.debug('auth.before_request,endpoint %s', request.endpoint)
        app.logger.debug('auth.before_request,blueprint %s', request.blueprint)
        if not current_user.confirmed \
            and request.endpoint \
            and request.endpoint != 'static' \
            and request.blueprint != 'auth' \
            and request.blueprint != 'react' \
            and request.blueprint != 'reactapi':
            # and not request.path.startswith('/static/'):
            # Huom. is_authenticated: kirjautunut
            # Kirjautuneet vahvistamattomat käyttäjät ohjataan muualta paitsi
            # reactapi-blueprintista unconfirmed.html-sivulle
            app.logger.debug('auth.before_request,path %s', request.path)
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    app = current_app._get_current_object()
    app.logger.debug('auth.unconfirmed,endnode: %s',request.endpoint)
    if current_user.is_anonymous or current_user.confirmed:
        app.logger.debug('auth.unconfirmed,redirect: %s',current_user.is_anonymous)
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            if not user.active:
                flash('Pääsy on tilapäisesti estetty.') 
                return render_template('auth/login.html', form=form)
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        else:
            flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Huom. Tässä on välitetty patterns-muuttuja, joka on määritelty forms.py:ssä.
    Tätä ei kuitenkaan tarvittaisi, vaan lomakekentän Regexp-validaattorin regex-ominaisuus
    saadaan jinja2-muuttujaan kentän validators[i].regex.pattern-ominaisuudesta 
    validators[i] ollessa Regexp, ks. oma wtf.html-tiedosto. 
    '''
    print("pattern:",patterns)
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, patterns=patterns)


@auth.route('/confirm/<token>')
@login_required
# Huom. login_required vie login-sivulle, ja kirjautuminen takaisin tänne
def confirm(token):
    app = current_app._get_current_object()
    app.logger.debug('/confirm,confirmed: %s',current_user.confirmed)
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        app.logger.debug('/confirm,confirmed here')
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
