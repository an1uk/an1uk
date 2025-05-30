# routes\auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from an1uk.models import db, User
from an1uk.forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('auth.register'))
        new_user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            email=form.email.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_approved:
                flash('Account pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password', 'danger')
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))


# Old registration route commented out
# This is replaced by the new registration route using Flask-WTF forms
# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists.', 'warning')
#             return redirect(url_for('auth.register'))
#         db.session.add(User(username=username, password=generate_password_hash(password)))
#         db.session.commit()
#         flash('Registration successful. Please log in.', 'success')
#         return redirect(url_for('auth.login'))
#     return render_template('register.html')


# Old login route commented out
# This is replaced by the new login route using Flask-WTF forms
# This route is not used in the current codebase, but kept for reference
# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             if not user.is_approved:
#                 flash('Account pending admin approval.', 'warning')
#                 return redirect(url_for('auth.login'))
#             login_user(user)
#             return redirect(url_for('main.index'))
#         flash('Invalid username or password', 'danger')
#     return render_template('login.html')

