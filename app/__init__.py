from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load config
app.config.from_object('config')

# Define database
db = SQLAlchemy(app)

# Build database
db.create_all()

@app.route("/")
def index():
    return render_template("index.html")
