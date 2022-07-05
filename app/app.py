from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError
from wtforms import Form, StringField, PasswordField, validators, EmailField

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

    def __init__(self, uname, password, email):
        self.username = uname
        self.password = password
        self.email = email


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
            return render_template("profile.html", user=user)
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
    form = UserRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User(form.username.data, form.email.data, form.password.data)
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
