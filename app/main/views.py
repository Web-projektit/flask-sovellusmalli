from flask import render_template, redirect, jsonify, url_for, abort, flash, \
     current_app, request, send_from_directory, send_file, Response, make_response
from flask_login import login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..email import send_email
from ..decorators import admin_required,debuggeri, token_required
import os, json, boto3
from botocore.client import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
# from azure.core.exceptions import ResourceNotFoundError
# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
from flask_weasyprint import HTML, render_pdf
from datetime import datetime
from io import BytesIO

ALLOWED_EXTENSIONS = { 'pdf', 'png', 'jpg', 'jpeg', 'gif' }

@debuggeri
def shorten(filename):
    # parts = filename.split('.') 
    name, extension = os.path.splitext(filename)
    length = 64 - len(extension)
    return name[:length] + extension

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def tee_kuvanimi(id,kuva):
    if id and kuva:
        return str(id) + '_' + kuva
    else:
        return ''

def poista_vanha_kuva(id,kuva):
    kuvanimi = tee_kuvanimi(id,kuva)
    app = current_app._get_current_object()
    KUVAPALVELU = app.config['KUVAPALVELU']
    KUVAPOLKU = app.config['KUVAPOLKU']
    filename = os.path.join(KUVAPOLKU, kuvanimi)
    if KUVAPALVELU == 'Azure':
        # Azure Blob Storage
        try:
            blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
            container_client = blob_service_client.get_container_client(app.config['AZURE_STORAGE_CONTAINER'])
            blob_client = container_client.get_blob_client(filename)
            blob_client.delete_blob()
        except Exception as e:
            app.logger.info(e)
            return False
        else:
            return True
    else:
        print("POISTETAAN:"+filename)
        try:
            os.remove(filename)
        except Exception as e:
            app.logger.info(e)
            return False
        else:   
            return True

def generate_token(user_id):
    app = current_app._get_current_object()
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id})

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/img/')
@main.route('/img/<path:filename>')
def img(filename = None):
    # Profiilikuvat Flask-sovelluskansiossa profiilikuvat,
    # paitsi oletusprofiilikuva static-kansiossa.
    # Huom. S3-kuvapalvelun toteutus on kesken
    app = current_app._get_current_object()
    KUVAPALVELU = app.config['KUVAPALVELU']
    KUVAPOLKU = app.config['KUVAPOLKU']
    app.logger.info("IMG:"+str(filename))
    if filename is None:
        return send_from_directory('static','default_profile.png')
    elif KUVAPALVELU == 'Azure':
        # Azure Blob Storage, anonyymi lukuoikeus blobiin
        filename = os.path.join(KUVAPOLKU,filename)
        try:
            # Azure Blob Storage setup
            CONTAINER = app.config['AZURE_STORAGE_CONTAINER']
            blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
            blob_client = blob_service_client.get_blob_client(container=CONTAINER, blob=filename)

            # Get the blob's data
            blob_data = blob_client.download_blob()
            data = blob_data.readall()
            return Response(data, mimetype=blob_data.properties.content_settings.content_type)

        except Exception as e:
            app.logger.exception("Virhe kuvan lähetyksessä Azure Blob Storagesta")
            app.logger.info(e)
            abort(404)
    else:
        # elif KUVAPALVELU == 'local' or KUVAPALVELU == 'AzureHome':
        # Lähetä tiedosto (vain, jos se olemassa)
        return send_from_directory(KUVAPOLKU, filename)      
    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.img:
        kuva = tee_kuvanimi(current_user.id,current_user.img) 
    else:
        kuva = '' 
    print("KUVA:"+kuva)
    return render_template('user.html', user=user, kuva=kuva)


# Tätä tarvittaisiin vain ilman profiilikuvaa
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile-all/', methods=['GET', 'POST'])
@login_required
def edit_profile_all():
    # Profiili, jossa on myös profiilikuva
    user = User.query.get_or_404(current_user.id)    
    form = EditProfileForm(obj=user)
    app = current_app._get_current_object()
    KUVAPALVELU = app.config['KUVAPALVELU']
    KUVAPOLKU = app.config['KUVAPOLKU']
    if form.validate_on_submit():
        # check if the post request has the file part
        kuvanimi = form.img.data
        if kuvanimi and current_user.img and kuvanimi != current_user.img:
            poista_vanha_kuva(current_user.id,current_user.img)
        if 'file' in request.files and file.filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Lomakkeelta lähetettynä paikallinen tallennus,
                # S3- ja Azure-tallennus tehty erikseen Javascriptillä
                kuvanimi = shorten(secure_filename(file.filename))
                filename = tee_kuvanimi(current_user.id,kuvanimi)
                file.save(os.path.join(KUVAPOLKU, filename))
        form.populate_obj(user)
        user.img = kuvanimi
        # db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    if user.img:
        kuva = tee_kuvanimi(user.id,user.img) 
    else:
        kuva = ''    
    return render_template('edit_profile_S3.html', form=form, kuva=kuva)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(obj=user,user=user)
    print(str(user))
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/edit-profile_S3', methods=['GET', 'POST'])
@login_required
def edit_profile_S3():
    user = User.query.get_or_404(current_user.id)
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('edit_profile_S3.html', form=form)


@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    # users = User.query.all() 
    if request.form.get('painike'):
        users = request.form.getlist('users')
        if len(users) > 0:
            query_start = "INSERT INTO users (id,active) VALUES "
            query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
            query_values = ""
            active = request.form.getlist('active')
            for v in users:
                if v in active:
                    query_values += "("+v+",1),"
                else:
                    query_values += "("+v+",0),"
            query_values = query_values[:-1]
            query = query_start + query_values + query_end
            # print("\n"+query+"\n")
            # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
            db.session.execute(query)
            db.session.commit()
            # return query
            #return str(request.form.getlist('users')) + \
            #       "<br>" + \
            #        str(request.form.getlist('active'))
        else:
            flash("Käyttäjälista puuttuu.")
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.name).paginate(
        page=page, per_page=current_app.config['FS_POSTS_PER_PAGE'],
        error_out=False)
    lista = pagination.items
    return render_template('users.html',users=lista,pagination=pagination,page=page)

@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify(OK="käyttäjä on poistettu.")
    else:
        return jsonify(virhe="käyttäjää ei löydy.")

@main.route('/sign-s3/')
@login_required
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')
  AWS_REGION = os.environ.get('AWS_REGION') 
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')
  kuva = str(current_user.id) + '_' + file_name
  # s3 = boto3.client('s3')
  s3 = boto3.client('s3',
    config=Config(signature_version='s3v4'),
    region_name=AWS_REGION)
  
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = kuva,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )
  dump = json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, kuva)
  })
  return dump


@main.route('/save-local', methods=['GET', 'POST'])
@login_required
def save_local():
    # cwd = os.getcwd()
    # print("WORKING DIRECTORY:"+cwd)
    app = current_app._get_current_object()
    KUVAPALVELU = app.config['KUVAPALVELU']
    KUVAPOLKU = app.config['KUVAPOLKU']
    virhe = ''
    msg = ''
    errmsg = ''
    try:
        if 'file' in request.files:
            file = request.files['file']
    except Exception as e:
        app.logger.info(e)
        errmsg = "Virhe tiedoston vastaanotossa."
        return json.dumps({'virhe':errmsg})
    
    if file and file.filename != '' and allowed_file(file.filename):
        kuvanimi = shorten(secure_filename(file.filename))
        filename = tee_kuvanimi(current_user.id,kuvanimi)
        if KUVAPALVELU == 'Azure':
            # Azure Blob Storage
            filename = KUVAPOLKU + filename
            try:
                blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
                container_client = blob_service_client.get_container_client(app.config['AZURE_STORAGE_CONTAINER'])
                blob_client = container_client.get_blob_client(filename)
                blob_client.upload_blob(file)
            except Exception as e:
                app.logger.info(e)
                virhe = "Virhe tiedoston tallennuksessa."
            else:
                msg = f"Tiedosto tallennettiin nimellä {filename}."
        else:    
            file.save(os.path.join(KUVAPOLKU, filename))
        msg = f"Tiedosto tallennettiin nimellä {filename}."
    else:
        virhe = "Tiedostoa ei annettu."
    return jsonify({
        'img': kuvanimi,
        'msg': msg,
        'virhe': virhe
        })

@main.route('/pdf')
@main.route('/pdf/<int:email>')
@login_required
def pdf(email=True):
    # Tässä luodaan henkilökortti pdf-tiedostoksi, myös omaan sähköpostiin
    year = datetime.now().year
    user = User.query.get_or_404(current_user.id)    
    kuva = tee_kuvanimi(user.id,user.img) 
    voimassa = str(year) + u"–" + str(year + 1)
    opetusala = "Web programming"
    html = render_template('henkilokortti.html', user=user, kuva=kuva, voimassa=voimassa, opetusala=opetusala)
    # return html
    pdf = render_pdf(HTML(string=html))
    if email:
        pdf_stream = BytesIO(pdf.data)
        send_email(user.email, 'Henkilökortti','mail/henkilokortti',pdf_stream,"henkilokortti.pdf",user=user)
        flash("Henkilökortti on lähetetty sähköpostiisi.") 
        return redirect(url_for('.user', username=user.username))
    else:
        return pdf
    

@main.route('/henkilokortti')
@token_required
def henkilokortti(user_id):
# Tässä haetaan henkilökortti tokenin avulla    
    year = datetime.now().year
    user = User.query.get_or_404(user_id)    
    kuva = tee_kuvanimi(user.id,user.img) 
    voimassa = str(year) + u"–" + str(year + 1)
    opetusala = "Web programming"
    html = render_template('henkilokortti.html', user=user, kuva=kuva, voimassa=voimassa, opetusala=opetusala)
    pdf = render_pdf(HTML(string=html))
    pdf_stream = BytesIO(pdf.data)

    # Set the response with the PDF stream
    response = make_response(pdf_stream.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=henkilokortti.pdf'
    return response

@main.route('/henkilokortti_token')
@main.route('/henkilokortti_token/<int:user_id>')
@login_required
def henkilokortti_token(user_id=None):
# Tässä luodaan token henkilökortin hakemista varten
    if user_id is None:
        user_id = current_user.id
    token = generate_token(user_id)   
    return jsonify({'token': token})


