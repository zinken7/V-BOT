# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from app.api import blueprint
from flask import request
from flask.views import MethodView
from app import db, cache

from app.models import FacebookUser, Customer, Keyword, Wordbook, Welcome

from app.pymessenger.bot import Bot
from app.pymessenger.page import Page

from unidecode import unidecode
import psycopg2
import os
import json
import random
from decouple import config


# Receive webhook
class ReceiveWebhook(MethodView):

    def __init__(self):
        self.master = FacebookUser.query.first()
        self.bot = Bot(self.master.p_token, app_secret=self.master.app_secret, api_version=config('FB_API_VERSION'))
        self.page = Page(self.master.p_token, app_secret=self.master.app_secret, api_version=config('FB_API_VERSION'))
        self.VERIFY_TOKEN = self.master.verify_token
        self.welcome, self.limitdict, self.unlimitdict, self.wordbooks, self.comment, self.buttons, self.quickreplies = get_res_data()
        get_customer()

    def get(self):
        token = request.args.get("hub.verify_token")
        if token == self.VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token'

    def post(self):
        output = request.get_json()
        for event in output['entry']:
            if "changes" in event:
                feeds = event['changes']
                for feed in feeds:
                    if feed.get('field') == "feed" and feed['value'].get('item') == "comment" and feed['value'].get('verb') == "add":
                        comment_id = feed['value'].get('comment_id')
                        sender_id = feed['value']['from'].get('id')
                        sender_name = feed['value']['from'].get('name')
                        if comment_id and sender_id != self.master.p_id:
                            if cache.get(sender_id) is not None:
                                # hide comment
                                self.page.page_hide_comment(comment_id)
                            else:
                                reply_comment(
                                    self.page, comment_id, sender_id, sender_name, self.welcome, self.comment)

            elif "messaging" in event:
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'):
                        sender_id = message['sender']['id']
                        _sender_id = 'c'+sender_id
                        text = message['message'].get('text')
                        attachments = message['message'].get('attachments')
                        quick_reply = message['message'].get('quick_reply')
                        if quick_reply:
                            payload = quick_reply.get('payload')
                            if payload:
                                reply_payload(self.bot, sender_id, payload, self.wordbooks, self.welcome, self.buttons, self.quickreplies)
                            continue
                        if attachments:
                            text = 'default'
                        if text:
                            if cache.get(_sender_id) is None or cache.get(_sender_id) != text:
                                cache.set(_sender_id, text, timeout=120)
                                reply_message(self.bot, sender_id,
                                              unidecode(text).lower(), self.limitdict, self.unlimitdict, self.wordbooks, self.welcome, self.buttons, self.quickreplies)
                    elif message.get('postback'):
                        sender_id = message['sender']['id']
                        _sender_id = 'p'+sender_id
                        payload = message['postback'].get('payload')
                        if payload:
                            if cache.get(_sender_id) is None or cache.get(_sender_id) != payload:
                                cache.set(_sender_id, payload, timeout=120)
                                reply_payload(self.bot, sender_id, payload, self.wordbooks, self.welcome, self.buttons, self.quickreplies)
        return "Message Processed", 200

# Reply payload
def reply_payload(bot, sender_id, payload, wordbooks, welcome, buttons, quickreplies):
    if payload == 'get_started':
        # luu khach vao cache
        uid = sender_id
        triggered = False
        cache.set(uid, triggered, timeout=0)

        # Gui loi chao
        user_info = bot.get_user_info(sender_id)
        fullname = user_info['first_name'] + " " + user_info['last_name']
        get_mes = welcome
        get_mes_arr = get_mes.split("@@")
        welcome_mes = get_mes_arr[0]+fullname+get_mes_arr[1]
        bot.send_text_message(sender_id, welcome_mes)

        # Luu khach hang
        customer = Customer.query.filter_by(uid=sender_id).first()
        if not customer:
            content = Customer(uid, triggered)
            db.session.add(content)
            db.session.commit()
        else:
            customer.uid = sender_id
            customer.triggered = triggered
            db.session.commit()
    else:
        send_data(bot, sender_id, payload, wordbooks, buttons, quickreplies)

# Reply comment and message
def reply_comment(page, comment_id, sender_id, sender_name, welcome, comment):
    # luu khach vao cache
    uid = sender_id
    triggered = False
    cache.set(uid, triggered, timeout=0)

    # like
    page.page_like_comment(comment_id)
    # reply comment
    if cache.get("ssreply") is None or not cache.get("ssreply"):
        cmt_text = random.choice(comment)
        if '@@' in cmt_text:
            get_cmt_arr = cmt_text.split("@@")
            reply_cmt = get_cmt_arr[0]+sender_name+get_cmt_arr[1]
        else:
            reply_cmt = cmt_text
        page.page_reply_comment(comment_id, reply_cmt)
        cache.set("ssreply", True, timeout=60)
    # hide
    page.page_hide_comment(comment_id)
    # reply private
    get_mes_arr = welcome.split("@@")
    welcome_mes = get_mes_arr[0]+sender_name+get_mes_arr[1]
    page.send_message(comment_id, welcome_mes)

    # Luu khach hang
    customer = Customer.query.filter_by(uid=sender_id).first()
    if not customer:
        content = Customer(uid, triggered)
        db.session.add(content)
        db.session.commit()

    return 'success'

# Response incoming message
def reply_message(bot, sender_id, message, litmit_dict, unlitmited_dict, wordbooks, welcome, buttons, quickreplies):
    isCustomer = cache.get(sender_id)
    if isCustomer is None:
        # Luu khach hang vao cache truoc
        uid = sender_id
        triggered = False
        cache.set(uid, triggered, timeout=0)
        # Gui loi chao
        user_info = bot.get_user_info(sender_id)
        fullname = user_info['first_name'] + " " + user_info['last_name']
        get_mes = welcome
        get_mes_arr = get_mes.split("@@")
        welcome_mes = get_mes_arr[0]+fullname+get_mes_arr[1]
        bot.send_text_message(sender_id, welcome_mes)
        # else we can create the customer
        customer = Customer.query.filter_by(uid=sender_id).first()
        if not customer:
            content = Customer(uid, triggered)
            db.session.add(content)
            db.session.commit()

        return 'success'
    else:
        # da triggered: unlimmited
        if isCustomer:
            choice = check_keyword(unlitmited_dict, message)
            if choice:
                send_data(bot, sender_id, choice, wordbooks, buttons, quickreplies)
        # chua triggered: limited
        else:
            # luu khach vao cache
            cache.set(sender_id, True, timeout=0)
            # tra loi khach
            choice = check_keyword(litmit_dict, message) if check_keyword(
                litmit_dict, message) else 'default'
            send_data(bot, sender_id, choice, wordbooks, buttons, quickreplies)
            # set triggered
            customer = Customer.query.filter_by(uid=sender_id).first()
            if customer:
                customer.uid = sender_id
                customer.triggered = True
                db.session.commit()

        return 'success'

# Send data
def send_data(bot, sender_id, choice, text, buttons, quickreplies):
    for item in text[choice]:
        msg_content = item['scontent']
        if item['stype'] == 'text':
            bot.send_text_message(sender_id, msg_content)
            continue
        if item['stype'] == 'img':
            bot.send_action(sender_id, "typing_on")
            bot.send_image(sender_id, msg_content)
            bot.send_action(sender_id, "typing_on")
            continue
        if item['stype'] == 'vds':
            bot.send_action(sender_id, "typing_on")
            bot.send_video(sender_id, msg_content)
            bot.send_action(sender_id, "typing_on")
            continue
        if item['stype'] == 'button':
            bot.send_button_message(sender_id, item['stext'], buttons[msg_content]['buttons'])
            continue
        if item['stype'] == 'quickreplies':
            bot.send_quick_replies_message(sender_id, item['stext'], quickreplies[msg_content]['quick_replies'])
            continue

# Check block to response
def check_keyword(_check, message):
    for items in _check:
        for item in items['value']:
            if item in message:
                return items['name']
    return False

# Get response data
@cache.cached(timeout=0, key_prefix='response_data')
def get_res_data():
    # welcome data
    welcome = Welcome.query.first()
    welcome_data = ''
    if welcome:
        welcome_data = welcome.value
    # keyword data
    keyword_data = Keyword.query.first()
    limit = keyword_data.l_dict
    unlimit = keyword_data.u_dict
    limitdict = list(map(
        lambda x: {"name": x["name"], "value": get_text(x["value"])}, limit))
    unlimitdict = list(map(
        lambda x: {"name": x["name"], "value": get_text(x["value"])}, unlimit))
    # wordbook data
    books = Wordbook.query.first()
    books_json = json.loads(books.w_val)
    wordbook_list = {}
    for book in books_json:
        wordbook_list[book['name']] = book['content']
    for items in wordbook_list.values():
        i = 0
        while i < len(items):
            if items[i]['stype'] == 'quickreplies' or items[i]['stype'] == 'button':
                items[i]['stext'] = items[i-1]['scontent']
                # xoa gi tri truoc
                i-=1
                del items[i]
            i+=1
    conn = db_connect()
    cursor = conn.cursor()

    # comment data
    cursor.execute('SELECT * FROM comments')
    rows = cursor.fetchall()
    objects_list = []
    for row in rows:
        objects_list.append(row[1])
    comment_data = objects_list
    # button data
    cursor.execute('SELECT * FROM buttons')
    rows = cursor.fetchall()
    objects_list = {}
    for row in rows:
        bts = []
        for item in row[3]:
            bts.append({
                "type": item['stype'],
                "title": item['title'],
                "payload": item['block']
            })
        objects_list[row[2]] = {
            'text': row[1],
            'buttons': bts
        }
    buttons_data = objects_list
    # quickreplies data
    cursor.execute('SELECT * FROM quickreplies')
    rows = cursor.fetchall()
    objects_list = {}
    for row in rows:
        bts = []
        for item in row[3]:
            bts.append({
                "content_type": item['stype'],
                "title": item['title'],
                "payload": item['payload'],
                "image_url": item['image_url']
            })
        objects_list[row[2]] = {
            'text': row[1],
            'quick_replies': bts
        }
    quickreplies_data = objects_list
    conn.close()

    return welcome_data, limitdict, unlimitdict, wordbook_list, comment_data, buttons_data, quickreplies_data

# Get customer data
def get_customer():
    customer_data = cache.get('customer-data')
    if customer_data is None:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ')
        rows = cursor.fetchall()

        # Convert query to objects of key-value pairs
        objects_list = {}
        for row in rows:
            objects_list[row[1]] = row[2]
        cache.set_many(objects_list, timeout=0)
        customer_data = 'already'
        cache.set('customer-data', customer_data, timeout=0)
        conn.close()

    return True

'''
*Addition support function
'''
def get_text(x):
    return list(map(lambda y: y['text'], x))

# Connect to Database
def db_connect():
    conn_string = "host="+config('DB_HOST')+" dbname="+config(
        'DB_NAME')+" user="+config('DB_USERNAME')+" password="+config('DB_PASS')
    conn = psycopg2.connect(conn_string)
    return conn
