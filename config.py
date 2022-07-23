from os.path import join, dirname, realpath

DEBUG = True

BASE_DIR = dirname(realpath(__file__))

# Set file upload path to upload assets
FILE_UPLOAD_PATH = join(BASE_DIR, 'app', 'static')
# Set max file size is 4BM
MAX_CONTENT_LENGTH = 4 * 1024 * 1024

# SQLite DB connection string
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(BASE_DIR, 'app.db')

SECRET_KEY = '\xb6\xfc\xbc" \xee48\xcd\x0f\xa5y\xfb\x0f\x10\x06\xeb(VM)\xfal\x87'

# We are using exchangerate-api as a currency rate/conversion service
EXCHANGE_RATE_API_KEY = "23aeb35b1d25aab2cfb8eb8a"
BASE_CURRENCY = "USD"
EXCHANGE_RATE_API = "https://v6.exchangerate-api.com/v6/{0}/latest".format(EXCHANGE_RATE_API_KEY)

# Password alogorithms to encrypt password
PASSWORD_SCHEMES = ['md5_crypt']


class TestConfiguration(object):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'