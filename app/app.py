from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import CombinedMultiDict

from .utils import CurrencyConverter, login_required, save_file_locally

app = Flask(__name__)

# Load config
app.config.from_object('config')
db = SQLAlchemy(app)

from .model import User, UserWallet
from .forms import UserRegistrationForm, EditUserRegistrationForm, UserLoginForm, UserWalletForm, TransferMoneyForm

# TODO: use proper error handlng if user directly hit any API like /user, /wallet

@app.route("/")
def index():
    """Default index route"""
    return render_template("index.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    """User login route to authenticate user and redirect to user panel"""
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
@login_required
def logout():
    """Remove session data and logout the user"""
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    """Signup route for user which read form data from the request and store into database"""

    # Combine files and form to upload profile photo of user
    form = UserRegistrationForm(CombinedMultiDict((request.files, request.form)))
    print("form.validate()>>>>>", form.validate(), request.form)
    if request.method == 'POST' and form.validate():
        try:
            save_file, profile_photo_name = save_file_locally(form, app)
            if save_file:
                user = User(form.username.data, form.password.data, form.email.data, profile_photo_name, form.default_currency.data)
                db.session.add(user)
                db.session.commit()
                flash('User added sucessfully, please login')
                return redirect(url_for('login'))
            else:
                err_msg = "Error while adding new user"
                flash(err_msg)
        except IntegrityError:
            # Roll back the transaction is user is alredy exist in the database
            db.session.rollback()
            flash('User already exists!')
        except Exception as e:
            app.logger.error("Error while storing user details", e)
    return render_template('signup.html', form=form)

@app.route("/static/<path:path>")
def static_dir(path):
    """This function is use to send static files to Flask HTML """
    return send_from_directory("static", path)

@app.route('/profile', methods =['GET', 'POST'])
@login_required
def profile():
    """User profile route to get/update user data"""
    form = EditUserRegistrationForm(CombinedMultiDict((request.files, request.form)))
    user = User.get_user(session['username'])
    if request.method == 'POST':
        try:
            save_file, profile_photo_name = save_file_locally(form, app)
            if save_file:
                user.username = form.username.data
                user.email = form.email.data
                # TODO: Remove existing user profile pic file on update
                user.profile_photo_url = profile_photo_name
                # TODO: update wallet amount if currency gets updated
                user.default_currency = form.default_currency.data
                db.session.commit()
                app.logger.info("User info of user '%s' updated sucessfully" % user.username)
                flash('User info updated successfully, you may need to relogin the application')
                return redirect(url_for('logout'))
            else:
                err_msg = "Error while updating user's info"
                flash(err_msg)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error while updating user info", e)
            flash('Failed to update user info')
        return render_template("user_profile.html", user=user, form=form, currency_choices=CurrencyConverter(app).get_all_currencies())
    else:
        if user:
            form.username.data = user.username
            form.email.data = user.email
            form.profile_photo.data = user.profile_photo_url
            form.default_currency.data = user.default_currency 
            return render_template("user_profile.html", user=user, form=form, currency_choices=CurrencyConverter(app).get_all_currencies())
        else:
            app.logger.error("User not found in the database, you might have updated the user's info.")
            return redirect(url_for('logout'))


@app.route('/wallet', methods =['GET', 'POST'])
@login_required
def wallet():
    """User wallet where user can transfer money to another user"""
    form = UserWalletForm(request.form)
    user = User.get_user(session['username'])
    user_wallet = db.session.query(UserWallet).filter_by(user_id=user.id).first()
    if request.method == 'POST':
        try:
            user_wallet = UserWallet.get_user_wallet(user)
            if user_wallet:
                new_amount = float(user_wallet.amount) + float(form.amount.data)
                user_wallet.amount = new_amount
                db.session.commit()
                form.amount.data = new_amount
            else:
                amount = UserWallet(user.id, form.amount.data)
                db.session.add(amount)
                db.session.commit()
            msg = "Amount added to wallet successfully"
            app.logger.info(msg)
            flash(msg)
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            err_msg = "Failed to add money to wallet"
            app.logger.error(err_msg, e)
            flash(err_msg)
    else:
        form.amount.data = 0
        if user_wallet:
            form.amount.data = user_wallet.amount
    return render_template("user_wallet.html", user=user, form=form)

@app.route('/transfer_money', methods =['GET', 'POST'])
@login_required
def transfer_money():
    """This function is use to transfer money to another user"""
    # TODO: Avoid transfering amount to same/current/payer user
    form = TransferMoneyForm(request.form)
    payer_user = User.get_user(session['username'])
    payer_user_wallet =  UserWallet.get_user_wallet(payer_user)
    if request.method == 'POST':
        try:
            amt_to_be_transfer = form.transfer_amount.data
            if UserWallet.validate_amount(payer_user, amt_to_be_transfer):
                payee_user = User.get_user(form.transfer_amount_to_user.data)
                payee_user_wallet =  UserWallet.get_user_wallet(payee_user)
               
                # Get exchange rate for target currency
                exchange_rates = CurrencyConverter(app).get_exchange_rates(payer_user.default_currency)
                get_target_exchange_rate = exchange_rates["conversion_rates"][payee_user.default_currency]

                # Update wallet of payee user
                payee_user_new_amount = float(payee_user_wallet.amount) + (float(amt_to_be_transfer) * float(get_target_exchange_rate))
                UserWallet.update_user_wallet(payee_user_wallet, payee_user_new_amount)

                # Update wallet of payer user
                payer_user_new_amount = float(payer_user_wallet.amount) - float(amt_to_be_transfer)  
                UserWallet.update_user_wallet(payer_user_wallet, payer_user_new_amount)                  
               
                msg = "Amount transferred to user '{}' successfully".format(payee_user.username)
            else:
                msg = "Please enter valid amount"
            app.logger.info(msg)
            flash(msg)
            return redirect(url_for('transfer_money'))
        except Exception as e:
            db.session.rollback()
            err_msg = "Failed to transfer money to user"
            app.logger.error(err_msg, e)
            flash(err_msg)
    else:
        form.transfer_amount.data = 0
        form.transfer_amount_to_user.choices = [user.username for user in User.query.all()]
    return render_template("transfer_money.html", user=payer_user, user_wallet=payer_user_wallet, form=form)
