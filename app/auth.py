from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, LoginManager, current_user
from .models import User
from . import db
from functools import wraps
mk = 'glepp'

login_manager = LoginManager()


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                if (current_user.urole != role) and (role != "ANY"):
                    return login_manager.unauthorized()
            except AttributeError:
                return login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        master_key = request.form.get('master-key')
        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        if master_key == mk:
            new_user = User(email=email,
                            name=name,
                            password=generate_password_hash(password, method='sha256'),
                            urole='admin')
        elif not master_key:
            new_user = User(email=email,
                            name=name,
                            password=generate_password_hash(password, method='sha256'),
                            urole='user')
        else:
            flash('Invalid master-key')
            return redirect(url_for('auth.signup'))

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required()
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
