from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from wtforms import Form, StringField, PasswordField, validators

app = Flask(__name__)

# Load config
app.config.from_object('config')
db = SQLAlchemy(app)


# User registration form
class UserRegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Re-enter password')

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
    return render_template("login.html")

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    form = UserRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User added sucessfully, please login')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)
