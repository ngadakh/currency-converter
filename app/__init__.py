from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load config
app.config.from_object('config')

# Define database
db = SQLAlchemy(app)

# Build database
db.create_all()

@app.route("/")
def home():
    return "Welcome to Flask Currency Converter Project"