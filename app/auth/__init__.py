# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask import Blueprint

blueprint = Blueprint(
    'auth_blueprint',
    __name__,
    cli_group=None,
    url_prefix='',
    template_folder='templates'
)
