# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from app.api import blueprint
from app.api.controller import ReceiveWebhook

## Main function
facebook_view = ReceiveWebhook.as_view('facebook')
blueprint.add_url_rule('/facebook', methods=['GET', 'POST'], view_func=facebook_view)