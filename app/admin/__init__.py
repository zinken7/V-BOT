# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask import redirect, url_for, Blueprint
from flask_login import current_user

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='/dashboard',
    template_folder='templates',
    static_folder='static',
    static_url_path=''
)

@blueprint.before_request
def restrict_to_login():
	if not current_user.is_authenticated:
		return redirect(url_for('auth_blueprint.login'))