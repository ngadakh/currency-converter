import os

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# SQLite DB connection string
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SECRET_KEY = '\xb6\xfc\xbc" \xee48\xcd\x0f\xa5y\xfb\x0f\x10\x06\xeb(VM)\xfal\x87'