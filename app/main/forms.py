from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    img = HiddenField("img") 
    submit = SubmitField('Submit')
   

class EditProfileAdminForm(FlaskForm):
    # Huom. render_kw välittyy suoraan jinja2-een, ja on käytettävissä siellä
    # field.kw['class']-ominaisuutena, ks. oma wtf.html-tiedosto.
    '''
    field.label: The label of the form field. It can be rendered using {{ field.label }}.
    field.type: The type of the form field (e.g., StringField, PasswordField).
    field.name: The name attribute of the form field, which is used in the HTML <input> element.
    field.id: The id of the form field, typically used for <label> elements and JavaScript references.
    field.errors: A list of validation errors associated with the field.
    field.data: The data of the field, i.e., the value entered by the user.
    field.description: An optional description of the field, which can be set in the field definition.
    field() or field.render_kw: The method to render the field. You can pass additional parameters or use render_kw for HTML attributes like class, style, etc.
    field.required: A boolean indicating whether the field is required. It can be used for conditional rendering or validation messages.
    field.value: The current value of the field.
    '''

    email = StringField('Email',render_kw={"class":"class-oma"},validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9 _.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    role_id = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    confirmed = BooleanField('Confirmed')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        print("validate_email:"+field.data)
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
