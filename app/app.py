from os.path import join

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError
from wtforms import Form, StringField, PasswordField, validators, EmailField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load config
app.config.from_object('config')
db = SQLAlchemy(app)


# User registration form
class UserRegistrationForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Re-enter password', [validators.DataRequired()])
    profile_photo = FileField('Profile Photo', [FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

# User login form
class UserLoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

# User model
class User(db.Model):
    id  = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String, unique=True, nullable=False)
    profile_photo_url = db.Column(db.String, unique=True, nullable=True)

    def __init__(self, uname, password, email, photo_url):
        self.username = uname
        self.password = password
        self.email = email
        self.profile_photo_url = photo_url


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
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
def logout():
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    form = UserRegistrationForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        try:
            # Save user profile photo
            file_obj = form.profile_photo.data
            profile_photo_name = str(form.username.data) + "_" + secure_filename(file_obj.filename)
            profile_photo_full_path = join(app.config['FILE_UPLOAD_PATH'], 'profile', profile_photo_name)
            file_obj.save(profile_photo_full_path)

            user = User(form.username.data, form.email.data, form.password.data, profile_photo_full_path)
            db.session.add(user)
            db.session.commit()

            flash('User added sucessfully, please login')
            return redirect(url_for('login'))
        except IntegrityError:
            # Roll back the transaction is user is alredy exist in the database
            db.session.rollback()
            flash('User already exists!')
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)
