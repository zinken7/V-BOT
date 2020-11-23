# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from flask import Blueprint

blueprint = Blueprint(
    'api_blueprint',
    __name__,
    url_prefix='/api'
)

'''

blueprint = Blueprint(
    'api_blueprint',
    __name__,
    subdomain='api'
)
'''