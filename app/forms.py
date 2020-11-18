# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField
from wtforms.validators import DataRequired

## login and registration

class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login'   , validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login'        , validators=[DataRequired()])