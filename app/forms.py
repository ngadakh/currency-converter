from wtforms import Form, StringField, PasswordField, validators, EmailField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed

from .utils import CurrencyConverter
from .app import app
from .model import User

class UserRegistrationForm(Form):
    """User registration form to load as HTML with fields"""
    username = StringField('Username', [validators.DataRequired()])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Re-enter password', [validators.DataRequired()])
    profile_photo = FileField('Profile Photo', [FileRequired(), FileAllowed(['jpg', 'png'], 'Select images only!')])
    default_currency = SelectField('default_currency', choices=CurrencyConverter(app).get_all_currencies())


class EditUserRegistrationForm(Form):
    """Edit user registration form to load as HTML with fields"""
    username = StringField('Username', [validators.DataRequired()])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
    profile_photo = FileField('Profile Photo', [FileRequired(), FileAllowed(['jpg', 'png'], 'Select images only!')])
    default_currency = SelectField('default_currency', choices=CurrencyConverter(app).get_all_currencies())


class UserLoginForm(Form):
    """User login form"""
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class UserWalletForm(Form):
    """User wallet where user can transfer and add money"""
    amount = StringField("Amount", [validators.DataRequired()])


class TransferMoneyForm(Form):
    """Transfer money form"""
    transfer_amount = StringField("Amount to be transfer", [validators.DataRequired()])
    transfer_amount_to_user = SelectField('select_user', choices=[user.username for user in User.query.all()])
