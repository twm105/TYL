from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


MESSAGE = 'Password must be at least 8 characters long.'


class Password(object):
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            message = 'Field must be between {} and {} characters long.'.format(min, max)
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or (self.max != -1 and l > self.max):
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    forename = StringField(_l('Forename'), validators=[DataRequired()])
    surname = StringField(_l('Surname'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired(),
                                                         Password(min=8, message=MESSAGE)])
    password2 = PasswordField(
        _l('Confirm Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField(_l('Old Password'), validators=[DataRequired()])
    new_password = PasswordField(_l('New Password'), validators=[DataRequired(),
                                                                 Password(min=8, message=MESSAGE)])
    new_password2 = PasswordField(_l('Confirm New Password'), validators=[DataRequired(),
                                                                          EqualTo('new_password')])
    submit = SubmitField(_l('Update Password'))


class ChangeEmailForm(FlaskForm):
    old_email = StringField(_l('Old Email Address'), validators=[DataRequired(), Email()])
    new_email = StringField(_l('New Email Address'), validators=[DataRequired(), Email()])
    new_email2 = PasswordField(
        _l('Confirm New Email Address'), validators=[DataRequired(),
                                               EqualTo('new_email')])
    submit = SubmitField(_l('Change Email'))