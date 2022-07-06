from os.path import join, dirname, realpath

DEBUG = True

BASE_DIR = dirname(realpath(__file__))

# Set file upload path to upload assets
FILE_UPLOAD_PATH = join(BASE_DIR, 'app', 'assets')
# Set max file size is 4BM
MAX_CONTENT_LENGTH = 4 * 1024 * 1024

# SQLite DB connection string
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(BASE_DIR, 'app.db')

SECRET_KEY = '\xb6\xfc\xbc" \xee48\xcd\x0f\xa5y\xfb\x0f\x10\x06\xeb(VM)\xfal\x87'