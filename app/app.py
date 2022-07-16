from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

from sqlalchemy.exc import IntegrityError
from wtforms import Form, StringField, PasswordField, validators, EmailField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.datastructures import CombinedMultiDict

from .utils import CurrencyConverter, login_required, save_file_locally

app = Flask(__name__)

# Load config
app.config.from_object('config')
db = SQLAlchemy(app)

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

# User model
class User(db.Model):
    """User database model""" 
    __tablename__ = 'user'
    id  = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String, unique=True, nullable=False)
    profile_photo_url = db.Column(db.String, unique=True, nullable=True)
    default_currency = db.Column(db.String(100), unique=True, nullable = False)

    def __init__(self, uname, email, password, photo_url, default_currency):
        self.username = uname
        self.password = password
        self.email = email
        self.profile_photo_url = photo_url
        self.default_currency = default_currency


class UserWalletForm(Form):
    """User wallet where user can transfer and add money"""
    amount = StringField("Amount", [validators.DataRequired()])


# User wallet model
class UserWallet(db.Model):
    """User wallet database model"""
    __tablename__ = 'user_wallet'
    wallet_id = db.Column(db.Integer, primary_key = True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount


@app.route("/")
def index():
    """Default index route"""
    return render_template("index.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    """User login route to authenticate user and redirect to user panel"""
    form = UserLoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user:
            session['id'] = user.id
            session['username'] = user.username
            return render_template("user_panel.html", user=user)
        else:
            flash('Incorrect username/password')
            return redirect(url_for('login'))
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    """Remove session data and logout the user"""
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    """Signup route for user which read form data from the request and store into database"""

    # Combine files and form to upload profile photo of user
    form = UserRegistrationForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        try:
            save_file, profile_photo_name = save_file_locally(form, app)
            if save_file:
                user = User(form.username.data, form.email.data, form.password.data, profile_photo_name, form.default_currency.data)
                db.session.add(user)
                db.session.commit()
                flash('User added sucessfully, please login')
                return redirect(url_for('login'))
            else:
                err_msg = "Error while adding new user"
                flash(err_msg)
        except IntegrityError:
            # Roll back the transaction is user is alredy exist in the database
            db.session.rollback()
            flash('User already exists!')
        except Exception as e:
            app.logger.error("Error while storing user details", e)
    return render_template('signup.html', form=form)

@app.route("/static/<path:path>")
def static_dir(path):
    """This function is use to send static files to Flask HTML """
    return send_from_directory("static", path)

@app.route('/profile', methods =['GET', 'POST'])
@login_required
def profile():
    """User profile route to get/update user data"""
    form = EditUserRegistrationForm(CombinedMultiDict((request.files, request.form)))
    user = db.session.query(User).filter_by(username=session['username']).first()
    if request.method == 'POST':
        try:
            save_file, profile_photo_name = save_file_locally(form, app)
            if save_file:
                user.username = form.username.data
                user.email = form.email.data
                user.profile_photo_url = profile_photo_name
                user.default_currency = form.default_currency.data
                db.session.commit()
                app.logger.info("User info of user '%s' updated sucessfully" % user.username)
                flash('User info updated successfully, you may need to relogin the application')
                return render_template("user_panel.html", user=user)
            else:
                err_msg = "Error while updating user's info"
                flash(err_msg)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error while updating user info", e)
            flash('Failed to update user info')
        return render_template("user_profile.html", user=user, form=form, currency_choices=CurrencyConverter(app).get_all_currencies())
    else:
        if user:
            form.username.data = user.username
            form.email.data = user.email
            form.profile_photo.data = user.profile_photo_url
            form.default_currency.data = user.default_currency 
            return render_template("user_profile.html", user=user, form=form, currency_choices=CurrencyConverter(app).get_all_currencies())
        else:
            app.logger.error("User not found in the database, you might have updated the user's info.")
            return redirect(url_for('logout'))


@app.route('/wallet', methods =['GET', 'POST'])
@login_required
def wallet():
    """User wallet where user can transfer money to another user"""
    form = UserWalletForm(request.form)
    user = db.session.query(User).filter_by(username=session['username']).first()
    user_wallet = db.session.query(UserWallet).filter_by(user_id=user.id).first()
    if request.method == 'POST':
        try:
            user_wallet = db.session.query(UserWallet).filter_by(user_id=user.id).first()
            if user_wallet:
                # TODO: Try to use db.session.merge()
                new_amount = int(user_wallet.amount) + int(form.amount.data)
                user_wallet.amount = new_amount
                db.session.commit()
                form.amount.data = new_amount
            else:
                amount = UserWallet(user.id, form.amount.data)
                db.session.add(amount)
                db.session.commit()
            msg = "Amount added to wallet successfully"
            app.logger.info(msg)
            flash(msg)
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            err_msg = "Failed to add money to wallet"
            app.logger.error(err_msg, e)
            flash(err_msg)
    else:
        form.amount.data = 0
        if user_wallet:
            form.amount.data = user_wallet.amount
    return render_template("user_wallet.html", user=user, form=form)

