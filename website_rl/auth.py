from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import mongo
from flask_login import login_user, login_required, logout_user, current_user
import uuid

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = mongo.db.users.find_one({'email': email})
        if user:
            if check_password_hash(user['password'], password):
                flash('Logged in successfully!', category='success')
                # Create a User object from the MongoDB document
                user_obj = User(user)
                # Log in the user using Flask-Login
                login_user(user_obj, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check if a user with the same email already exists in MongoDB
        existing_user = mongo.db.users.find_one({'email': email})

        if existing_user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Hash the password and create a new user document in MongoDB
            hashed_password = generate_password_hash(password1, method='sha256')
            new_user = {
                'id': uuid.uuid4().hex,
                'email': email,
                'first_name': first_name,
                'password': hashed_password
            }
            mongo.db.users.insert_one(new_user)

            # Log in the newly created user
            user = mongo.db.users.find_one({'email': email})
            user_obj = User(user)
            login_user(user_obj, remember=True)

            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
