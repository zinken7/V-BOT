# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from app.admin import blueprint
from flask import render_template

from app.admin.controller import IndexView, CustomerView, WelcomeView, KeywordView, WordbookView, ButtonView, QuickRepliesView, AssetsView, CommentDataView, PersistentMenuView, SettingView, UploadView, DownloadView


## Main function
# Index View
index_view = IndexView.as_view('index')
blueprint.add_url_rule('/', methods=['GET', 'DELETE'], view_func=index_view)

# Customers View
customer_view = CustomerView.as_view('customers')
blueprint.add_url_rule('/customers', methods=['GET', 'POST'], view_func=customer_view)

# WelcomeView View
welcome_view = WelcomeView.as_view('welcomes')
blueprint.add_url_rule('/welcomes', methods=['POST'], view_func=welcome_view)
blueprint.add_url_rule('/welcomes', methods=['GET'], defaults={'id' : None}, view_func=welcome_view)
blueprint.add_url_rule('/welcomes/<id>', methods=['GET'], view_func=welcome_view)

# Keywords View
keyword_view = KeywordView.as_view('keywords')
blueprint.add_url_rule('/keywords', methods=['POST'], view_func=keyword_view)
blueprint.add_url_rule('/keywords', methods=['GET'], defaults={'id' : None}, view_func=keyword_view)
blueprint.add_url_rule('/keywords/<id>', methods=['GET'], view_func=keyword_view)

# Wordbook View
wordbook_view = WordbookView.as_view('wordbooks')
blueprint.add_url_rule('/wordbooks', methods=['POST'], view_func=wordbook_view)
blueprint.add_url_rule('/wordbooks', methods=['GET'], defaults={'id' : None}, view_func=wordbook_view)
blueprint.add_url_rule('/wordbooks/<id>', methods=['GET'], view_func=wordbook_view)

# Button Template View
button_view = ButtonView.as_view('buttons')
blueprint.add_url_rule('/buttons', methods=['GET', 'POST'], defaults={'id' : None}, view_func=button_view)
blueprint.add_url_rule('/buttons/<id>', methods=['GET', 'POST', 'DELETE'], view_func=button_view)

# QuickReplies View
quickreplies_view = QuickRepliesView.as_view('quick-replies')
blueprint.add_url_rule('/quick-replies', methods=['GET', 'POST'], defaults={'id' : None}, view_func=quickreplies_view)
blueprint.add_url_rule('/quick-replies/<id>', methods=['GET', 'POST', 'DELETE'], view_func=quickreplies_view)

# Assets View
assets_view = AssetsView.as_view('assets')
blueprint.add_url_rule('/assets', methods=['POST'], view_func=assets_view)
blueprint.add_url_rule('/assets', methods=['GET'], defaults={'id' : None}, view_func=assets_view)
blueprint.add_url_rule('/assets/<id>', methods=['GET', 'DELETE'], view_func=assets_view)

# CommentData View
comment_view = CommentDataView.as_view('comments')
blueprint.add_url_rule('/comments', methods=['GET', 'POST'], defaults={'id' : None}, view_func=comment_view)
blueprint.add_url_rule('/comments/<id>', methods=['GET', 'POST', 'DELETE'], view_func=comment_view)

# PersistentMenu View
persistentmenu_view = PersistentMenuView.as_view('persistent-menu')
blueprint.add_url_rule('/persistent-menu', methods=['PUT'], view_func=persistentmenu_view)
blueprint.add_url_rule('/persistent-menu', methods=['GET', 'POST', 'DELETE'], defaults={'id' : None}, view_func=persistentmenu_view)
blueprint.add_url_rule('/persistent-menu/<id>', methods=['GET', 'POST', 'DELETE'], view_func=persistentmenu_view)

# Setting View
setting_view = SettingView.as_view('settings')
blueprint.add_url_rule('/settings', methods=['DELETE'], view_func=setting_view)
blueprint.add_url_rule('/settings', methods=['GET', 'POST'], defaults={'id' : None}, view_func=setting_view)
blueprint.add_url_rule('/settings/<id>', methods=['GET', 'POST', 'PUT'], view_func=setting_view)

## Auth Api
# Upload files
upload_view = UploadView.as_view('upload')
blueprint.add_url_rule('/upload', methods=['POST'], view_func=upload_view)

# Upload files
download_view = DownloadView.as_view('download')
blueprint.add_url_rule('/download', methods=['GET'], defaults={'id' : None}, view_func=download_view)
blueprint.add_url_rule('/download/<id>', methods=['GET'], view_func=download_view)