from flask_sqlalchemy import SQLAlchemy
from .app import app

db = SQLAlchemy(app)

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

    @staticmethod
    def get_user(username):
        """This method used to get single user's details"""
        user = db.session.query(User).filter_by(username=username).first()
        return user


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

    @staticmethod
    def get_user_wallet(user):
        """This method is used to get user wallet details"""
        user_wallet = db.session.query(UserWallet).filter_by(user_id=user.id).first()
        return user_wallet
    
    @staticmethod
    def update_user_wallet(user_wallet, amount):
        """This method is used to update amount in user's wallet"""
        user_wallet.amount = round(amount, 2)
        db.session.commit()


    @staticmethod
    def validate_amount(user, amount):
        """This method is used to validate the amount from the wallet user wants to transfer"""
        user_wallet = UserWallet.get_user_wallet(user)
        if float(amount) <= float(user_wallet.amount):
            return True 
        else:
            return False
