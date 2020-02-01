from flask import (Blueprint, render_template, redirect, url_for, request, flash)
from flask_login import login_user, logout_user, login_required

from models.User import UserModel

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/login', methods=["POST"])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = UserModel.get_one(args={'email': email})

    if not user:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.login'))

    verify_pwd = user.verify_password(password)
    if verify_pwd.json['status'] == 403:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))


@auth.route('/signup')
def signup():
    return render_template("signup.html")


@auth.route('/signup', methods=["POST"])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = UserModel.check_for_conflict(args={'email': email})

    # if a user is found, we want to redirect back to signup page so user can try again
    if user.json['user']:
        flash('Email address already exists')
        return redirect((url_for("auth.signup")))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    hash_pwd = UserModel.generate_hash(password)
    new_user = UserModel({
        "email": email,
        "name": name,
        "password": hash_pwd,
        "is_active": True,
        "is_anonymous": False,
        "is_authenticated": True
    })

    new_user.save()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
