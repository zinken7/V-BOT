# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
import click
from app import db, login_manager
from app.auth import blueprint
from app.forms import LoginForm
from app.models import User, FacebookUser

from app.auth.util import verify_pass

@blueprint.route('/', methods=['GET', 'POST'])
def home_index():
    return redirect(url_for('auth_blueprint.login'))

## Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('auth_blueprint.login'))

        # Something (user or pass) is not ok
        return render_template( 'auth/accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'auth/accounts/login.html', form=login_form)
    
    return redirect(url_for('admin_blueprint.index'))

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_blueprint.login'))

@blueprint.route('/policy', methods=['GET'])
def policy():
    return render_template('auth/policy.html')

# CLI Command
@blueprint.cli.command('create')
@click.argument('username', nargs=1)
@click.argument('password', nargs=1)
def create_superuser(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo('Username was existed!')
    else:
        # else we can create the user
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        click.echo('User with username %s was created!' % (username))
    
@blueprint.cli.command('fb_app')
@click.argument('app_id', nargs=1)
@click.argument('app_secret', nargs=1)
@click.argument('verify_token', nargs=1)
def create_app_info(app_id, app_secret, verify_token):
    user = FacebookUser.query.first()
    if user:
        click.echo('An app was existed!')
    else:
        uid = 666888
        u_token = None
        p_id = None
        p_token = None
        # else we can create the user
        user = FacebookUser(uid, u_token, app_id, app_secret, verify_token, p_id, p_token)
        db.session.add(user)
        db.session.commit()
        click.echo('New app with ID: %s were added!' % (app_id))