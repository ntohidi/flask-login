from flask import (Blueprint, render_template, redirect, url_for, request, flash)
from flask_login import login_user, logout_user, login_required
from app.tools.email_man import send_email

from models.User import UserModel

import os

auth = Blueprint('auth', __name__)

# TODO read server from app config
server = "http://localhost:9090/"


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
    verification_code = os.urandom(5).hex()

    user_info = {
        "email": email,
        "name": name,
        "password": hash_pwd,
        "is_active": False,
        "is_anonymous": False,
        "is_authenticated": False,
        "verification_code": verification_code,
    }

    new_user = UserModel(user_info)
    new_user.save()

    user_info.pop("_id", "")
    html = render_template("emails/register.html", profile=user_info, server=server)
    send_email(subject="Thanks For Registering", html=html, user_email=email)

    flash('A confirmation email has been sent to your email, kindly verify your account')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/verify/<email>/<code>')
def verify_account(email, code):
    user = UserModel.get_one(args={"email": email})
    if user:
        _user = user.to_json()
        if bool(_user.get('verification_code', "")):
            if user.verification_code == code:
                user.update(
                    args={"email": email},
                    data={'$set': {'is_authenticated': True, 'is_active': True},
                          '$unset': {'verification_code': 1}}
                )
                return redirect(url_for('auth.login'))

            flash("Oh! wrong verification code!")
            return redirect(url_for('auth.login'))

        flash("You're account had been already verified!")
        return redirect(url_for('auth.login'))

    flash("No such a user with email {} found!".format(email))
    return redirect(url_for('auth.login'))


@auth.route('/forget')
def forget():
    return render_template("forget.html")


@auth.route('/forget', methods=["POST"])
def forget_post():
    email = request.form.get('email')
    user = UserModel.get_one(args={'email': email})

    if not user:
        flash("Please check your login details and try again")
        return redirect(url_for('auth.login'))

    reset_code = os.urandom(5).hex()
    user.update(
        args={'email': email},
        data={"$set": {'request_reset': True, 'reset_code': reset_code}}
    )

    # send reset password email
    html = render_template("emails/reset-password.html", email=email, server=server, code=reset_code)
    send_email(subject="Reset Password", html=html, user_email=email)

    flash("A reset link has been sent to your email, kindly check and reset your password")
    return redirect(url_for('auth.login'))


@auth.route('/reset/<email>/<code>')
def reset(email, code):
    user = UserModel.get_one(args={'email': email, 'request_reset': True})
    if user and user.request_reset:
        if user.reset_code == code:
            return render_template("reset.html", email=email)
    flash("Reset password link is expired")
    return redirect(url_for('auth.login'))


@auth.route('/reset', methods=["POST"])
def reset_post():
    email = request.form.get('email')
    pwd = request.form.get('password')
    conf_pwd = request.form.get('conf_password')

    if pwd != conf_pwd:
        flash("Passwords don't math")
        return redirect(url_for('auth.reset', email=email))

    user = UserModel.get_one(args={'email': email, 'request_reset': True})

    if not user:
        flash("No such a user with email {} found".format(email))
        return redirect(url_for('auth.login'))

    hash_pwd = UserModel.generate_hash(pwd)
    user.update(
        args={'email': email, 'request_reset': True},
        data={
            "$set": {'password': hash_pwd},
            '$unset': {'request_reset': 1, 'reset_code': 1}
        }
    )

    return redirect(url_for('auth.login'))
