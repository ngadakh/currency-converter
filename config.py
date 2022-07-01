import os

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# SQLite DB connection string
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}
