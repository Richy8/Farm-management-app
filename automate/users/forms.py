from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from automate.models import User


class NewUserForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field is Required'),
                Email(message='Invalid Email')])
    role = SelectField('Role', choices=[('', 'Select User Role'),
                ('Admin','Admin'), ('Viewer', 'Viewer'), ('Account','Account'), ('Procurement','Procurement'), ('Sales','Sales'), ('Feedmill','Feedmill'), ('Store','Store'), ('Egg-Store','Egg-Store'), ('Human Resource','Human Resource')])
    submit = SubmitField('ADD USER')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field is Required'),
                Email(message='Invalid Email')])
    username = StringField('Username', validators=[InputRequired(message='Field is Required'),
                Length(min=6, message='Username is too short')])
    password = PasswordField('Password', validators=[
                InputRequired(message='Field is Required'), Length(min=6, message='Password must be at least 6 characters')])
    submit = SubmitField('SIGNUP')

    def validate_username(self, username):
        user_check = User.query.filter_by(username=username.data).first()
        if user_check:
            raise ValidationError('Username already Exist')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field is Required'),
                Email(message='Invalid Email')])
    password = PasswordField('Password', validators=[
                InputRequired(message='Field is Required'), Length(min=6, message='Password must be at least 6 characters')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('LOGIN')

class ForgetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(message='Field is Required'),
                Email(message='Invalid Email')])
    submit = SubmitField('RETRIEVE')

    def validate_email(self, email):
        email_check = User.query.filter_by(email=email.data).first()
        if email_check is None:
            raise ValidationError('Email does not exist')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[
                InputRequired(message='Field is Required'), Length(min=6, max=12, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password',
                validators=[InputRequired(message='Field is Required'), EqualTo('password')])
    submit = SubmitField('RESET')

class ProfileForm(FlaskForm):
    firstname = StringField('Firstname')
    lastname = StringField('Lastname')
    email = StringField('Email')
    username = StringField('Username', validators=[InputRequired(message='Field is Required'),
                Length(min=6, message='Username is too short')])
    role = StringField('Role')
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg','png','jpeg','JPEG', 'JPG'])])
    submit = SubmitField('UPDATE')
