# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2020 -zinken7
"""

from app.admin import blueprint
from flask import render_template, request, jsonify, abort, send_file, url_for
from flask.views import MethodView
from app import db, cache

from app.models import Customer, Asset, Keyword, Wordbook, ButtonData, QuickReplies, Welcome, CommentData, FacebookUser, FacebookPage, PersistentMenu
from app.pypage.token import Token
from app.pymessenger.page import Page

from werkzeug.utils import secure_filename
from flask import current_app as app

import os
import json
import collections
import psycopg2
from decouple import config


# Index
class IndexView(MethodView):

    def get(self):
        return render_template('admin/index.html')

    def delete(self):
        try:
            cache.clear()
            return jsonify(title="Success! ", message="Xóa cache thành công", status="success")
        except:
            return jsonify(title="Fail! ", message="Tải lại trang và thử lại...", status="danger")

# Customer
class CustomerView(MethodView):

    def get(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM "customers" ORDER BY "id" DESC LIMIT 10')
        rows = cursor.fetchall()

        # Convert query to objects of key-value pairs
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d["id"] = row[0]
            d["uid"] = row[1]
            d["triggered"] = row[2]
            objects_list.append(d)

        data = objects_list
        conn.close()

        return render_template('admin/customers.html', data=data)

    def post(self):
        # Loading customer to database
        try:
            filename = 'customer.csv'
            document_path = os.path.join(
                app.config['UPLOAD_FILE'], filename)
            conn = db_connect()
            cursor = conn.cursor()
            with open(document_path, 'r') as f:
                next(f)
                cursor.copy_from(f, 'customers', sep=',',
                                    columns=('uid', 'triggered'))
            conn.commit()
            conn.close()

            return jsonify(title="Success! ", message="Bạn đã tải lên khách hàng mới thành công", status="success")

        except:
            return jsonify(title="Fail! ", message="Tải lên khách hàng không thành công", status="danger")

# Welcome Message
class WelcomeView(MethodView):

    def get(self, id):
        if id:
            data = Welcome.query.first()
            if data:
                response = data.value
            else:
                response = ''
            return jsonify(response)

        return render_template('admin/welcomes.html')

    def post(self):
        input_d = request.get_json()
        data = Welcome.query.first()
        if data:
            data.value = input_d['data']
            db.session.commit()
        # else we can create
        else:
            content = Welcome(input_d['data'])
            db.session.add(content)
            db.session.commit()

        return jsonify(title="Success! ", message="Cập nhật lời chào thành công", status="success")

# Keyword
class KeywordView(MethodView):

    def get(self, id):
        if id:
            data = Keyword.query.first()
            # Convert query to objects of key-value pairs
            objects_list = {'l_dict': [], 'u_dict': []}

            if not data:
                return jsonify(objects_list)

            objects_list['l_dict'] = data.l_dict
            objects_list['u_dict'] = data.u_dict

            response = objects_list
            return jsonify(response)

        return render_template('admin/keywords.html')

    def post(self):
        input_d = request.get_json()
        self.l_dict = input_d['l_dict']
        self.u_dict = input_d['u_dict']

        keywords = Keyword.query.first()
        if keywords:
            keywords.l_dict = self.l_dict
            keywords.u_dict = self.u_dict
            db.session.commit()
        # else we can create
        else:
            content = Keyword(self.l_dict, self.u_dict)
            db.session.add(content)
            db.session.commit()

        return jsonify(title="Success! ", message="Cập nhật từ khóa thành công", status="success")

# Wordbook
class WordbookView(MethodView):

    def get(self, id):
        if id:
            try:
                books = Wordbook.query.first()
                response = json.loads(books.w_val)
                return jsonify(response)
            except:
                demo_data = [{
                    "name": "default",
                    "content": [{
                        "stype": "img",
                        "scontent": "Demo thư viện",
                    }
                    ]
                }
                ]
                self.w_val = json.dumps(demo_data)
                content = Wordbook(self.w_val)
                db.session.add(content)
                db.session.commit()

                return jsonify(demo_data)

        return render_template('admin/wordbooks.html')

    def post(self):
        word_data = request.get_json()
        final = json.dumps(word_data['data'])
        books = Wordbook.query.first()
        books.w_val = final

        db.session.commit()
        return jsonify(title="Success! ", message="Cập nhật thư viện thành công", status="success")

# Button
class ButtonView(MethodView):

    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM buttons ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "name": row[1], "u_name": row[2], "val": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)
        return render_template('admin/buttons.html')

    def post(self, id):
        if id:
            data = ButtonData.query.filter_by(id=id).first()
            if data:
                input_d = request.get_json()
                data.name = input_d['name']
                data.u_name = input_d['u_name']
                data.val = input_d['val']
                db.session.commit()
                return jsonify(title="Success! ", message="Cập nhật mẫu thành công", status="success")
            else:
                return jsonify(title="Fail! ", message="Cập nhật mẫu không thành công", status="danger")
        else:
            input_d = request.get_json()
            add_name = input_d['name']
            add_u_name = input_d['u_name']
            add_val = []
            content = ButtonData(add_name, add_u_name, add_val)
            db.session.add(content)
            db.session.commit()

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM buttons ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "name": row[1], "u_name": row[2], "val": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)

    def delete(self, id):
        data = ButtonData.query.filter_by(id=id).first()
        if data:
            db.session.delete(data)
            db.session.commit()
            return jsonify(title="Success! ", message="Đã xóa mẫu", status="success")
        else:
            return jsonify(title="Fail! ", message="Load lại trang và thử lại..", status="danger")

# Quick Replies
class QuickRepliesView(MethodView):

    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quickreplies ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "name": row[1], "u_name": row[2], "val": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)
        return render_template('admin/quick_replies.html')

    def post(self, id):
        if id:
            data = QuickReplies.query.filter_by(id=id).first()
            if data:
                input_d = request.get_json()
                data.name = input_d['name']
                data.u_name = input_d['u_name']
                data.val = input_d['val']
                db.session.commit()
                return jsonify(title="Success! ", message="Cập nhật mẫu thành công", status="success")
            else:
                return jsonify(title="Fail! ", message="Cập nhật mẫu không thành công", status="danger")
        else:
            input_d = request.get_json()
            add_name = input_d['name']
            add_u_name = input_d['u_name']
            add_val = []
            content = QuickReplies(add_name, add_u_name, add_val)
            db.session.add(content)
            db.session.commit()

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quickreplies ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "name": row[1], "u_name": row[2], "val": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)

    def delete(self, id):
        data = QuickReplies.query.filter_by(id=id).first()
        if data:
            db.session.delete(data)
            db.session.commit()
            return jsonify(title="Success! ", message="Đã xóa mẫu", status="success")
        else:
            return jsonify(title="Fail! ", message="Load lại trang và thử lại..", status="danger")

# Assets
class AssetsView(MethodView):

    def __init__(self):
        self.master = FacebookUser.query.first()
        self.page = Page(self.master.p_token,
                         api_version=config('FB_API_VERSION'))

    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM assets')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append(
                    {"id": row[0], "key": row[1], "val": row[2]})

            data = objects_list
            conn.close()

            return jsonify(data)

        else:
            return render_template('admin/assets.html')

    def post(self):
        input_data_set = request.get_json()
        if not input_data_set:
            return 'Wrong!!!'
        input_data = input_data_set['data']
        self.id = input_data['id']
        self.a_key = input_data['key']
        self.a_val = input_data['val']

        # send to fb to get attrid
        document_path = request.url_root+'static/uploads/media/'+self.a_key
        if '.mp4' not in self.a_key:
            att_img = self.page.upload_file(document_path, 'image')
            self.a_val = att_img['attachment_id']
        else:
            att_vds = self.page.upload_file(document_path, 'video')
            self.a_val = att_vds['attachment_id']

        # update the asset in DB
        data_asset = Asset.query.filter_by(id=self.id).first()
        if data_asset:
            data_asset.a_key = self.a_key
            data_asset.a_val = self.a_val
            db.session.commit()

        # send data back to client
        data = self.a_val

        return jsonify(data)

    def delete(self, id):
        delData = Asset.query.filter_by(id=id).first()
        if delData:
            if '.csv' not in delData.a_key:
                os.remove(os.path.join(
                    app.config['UPLOAD_MEDIA'], delData.a_key))
            else:
                os.remove(os.path.join(
                    app.config['UPLOAD_FILE'], delData.a_key))
            db.session.delete(delData)
            db.session.commit()
            return jsonify(title="Success! ", message="Đã xóa file", status="success")
        else:
            return jsonify(title="Fail! ", message="Load lại trang và thử lại..", status="danger")

# Comment Data
class CommentDataView(MethodView):

    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM comments ')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "value": row[1]})
            data = objects_list
            conn.close()

            return jsonify(data)
        return render_template('admin/comments.html')

    def post(self, id):
        if id:
            data = CommentData.query.filter_by(id=id).first()
            if data:
                input_d = request.get_json()
                data.value = input_d['data']
                db.session.commit()
                return jsonify(title="Success! ", message="Cập nhật trả lời thành công", status="success")
            else:
                return jsonify(title="Fail! ", message="Cập nhật không thành công", status="danger")
        else:
            add_val = ''
            content = CommentData(add_val)
            db.session.add(content)
            db.session.commit()

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM comments ')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "value": row[1]})
            data = objects_list
            conn.close()

            return jsonify(data)

    def delete(self, id):
        data = CommentData.query.filter_by(id=id).first()
        if data:
            db.session.delete(data)
            db.session.commit()
            return jsonify(title="Success! ", message="Đã xóa bình luận", status="success")
        else:
            return jsonify(title="Fail! ", message="Load lại trang và thử lại..", status="danger")

# Persistent Menu
class PersistentMenuView(MethodView):

    def __init__(self):
        self.user = FacebookUser.query.first()
        self.page = Page(self.user.p_token, api_version=config('FB_API_VERSION'))

    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM per_menus ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "stype": row[1], "title": row[2], "block": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)
        else:
            return render_template('admin/persistent_menu.html')

    def post(self, id):
        if id:
            data = PersistentMenu.query.filter_by(id=id).first()
            if data:
                input_d = request.get_json()

                data.stype = input_d['stype']
                data.title = input_d['title']
                data.block = input_d['block']
                db.session.commit()
                return jsonify(title="Success! ", message="Cập nhật menu thành công", status="success")
            else:
                return jsonify(title="Fail! ", message="Cập nhật menu không thành công", status="danger")
        else:
            stype = 'postback'
            title = ''
            block = ''
            content = PersistentMenu(stype, title, block)
            db.session.add(content)
            db.session.commit()

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM per_menus ORDER BY id')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append({"id": row[0], "stype": row[1], "title": row[2], "block": row[3]})
            data = objects_list
            conn.close()

            return jsonify(data)

    def put(self):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM per_menus ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        if len(rows) > 0:
            payload = []
            for row in rows:
                if row[1] == "postback":
                    payload.append(
                        {
                            "type": "postback",
                            "title": row[2],
                            "payload": row[3]
                        }
                    )
                else:
                    payload.append(
                        {
                            "type": "web_url",
                            "title": row[2],
                            "url": row[3],
                            "webview_height_ratio": "full"
                        }
                    )
            data = {
                "persistent_menu": [
                    {
                        "locale": "default",
                        "composer_input_disabled": False,
                        "call_to_actions": payload
                    }
                ]
            }
            self.page.set_persistent_menu(data)
            return jsonify(title="Success! ", message="Đăng ký Persistent Menu thành công", status="success")
        else:
            return jsonify(title="Fail! ", message="Cần có ít nhất 1 menu..", status="danger")

    def delete(self, id):
        if id:
            data = PersistentMenu.query.filter_by(id=id).first()
            if data:
                db.session.delete(data)
                db.session.commit()
                return jsonify(title="Success! ", message="Đã xóa menu!", status="success")
            else:
                return jsonify(title="Fail! ", message="Load lại trang và thử lại..", status="danger")
        else:
            self.page.remove_persistent_menu()
            return jsonify(title="Success! ", message="Hủy đăng ký thành công", status="success")

# Setting
class SettingView(MethodView):

    def __init__(self):
        self.user = FacebookUser.query.first()
        self.token = Token(self.user.app_id, user_id=self.user.uid,
                           app_secret=self.user.app_secret, api_version=config('FB_API_VERSION'))

    def get(self, id):
        if id:
            try:
                # return page list
                conn = db_connect()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM facebookpages')
                rows = cursor.fetchall()

                # Convert query to objects of key-value pairs
                objects_list = []
                for row in rows:
                    objects_list.append(
                        {"uid": row[1], "avatar": row[2], "name": row[3], "selected": row[4]})

                data = objects_list
                conn.close()

                return jsonify(data)
            except:
                return jsonify([])
        return render_template('admin/settings.html', appID=self.user.app_id, version=config('FB_API_VERSION'))

    def post(self):
        input_data = request.get_json()
        # luu user token va user id
        self.user.u_token = input_data['token']
        self.user.uid = input_data['uid']
        db.session.commit()

        # lay danh sach page
        try_times = 0
        while try_times < 3:
            try:
                listpages = self.token.get_page(self.user.u_token)
                # register app
                callback_url = request.url_root[:-1] + \
                    url_for('api_blueprint.facebook')
                self.token.register_app_fields(
                    callback_url, self.user.verify_token, 'feed,messages,messaging_postbacks,message_reads')
                break
            except:
                try_times += 1
        for page in listpages:
            uid = page['id']
            if not FacebookPage.query.filter_by(uid=uid).first():
                avatar = page['picture']['data']['url']
                name = page['name']
                selected = False
                # else we can create the customer
                content = FacebookPage(uid, avatar, name, selected)
                db.session.add(content)
                db.session.commit()

        # tra ve danh sach page
        try:
            # return page list
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM facebookpages')
            rows = cursor.fetchall()

            # Convert query to objects of key-value pairs
            objects_list = []
            for row in rows:
                objects_list.append(
                    {"uid": row[1], "avatar": row[2], "name": row[3], "selected": row[4]})

            data = objects_list
            conn.close()

            return jsonify(data)
        except:
            return jsonify([])

    def put(self, id):
        page_id = id
        # longlived token
        ll_token = self.token.get_ll_token(self.user.u_token)
        # page token
        page_token = self.token.get_page_token(ll_token, page_id)

        # save data to facebook user
        self.user.p_id = page_id
        self.user.p_token = page_token

        page_selected = FacebookPage.query.filter_by(uid=page_id).first()
        page_selected.selected = True
        db.session.commit()

        # welcome data
        welcome = Welcome.query.first()
        welcome_data = welcome.value
        if '@@' in welcome_data:
            get_cmt_arr = welcome_data.split("@@")
            reply_data = get_cmt_arr[0]+"{{user_full_name}}"+get_cmt_arr[1]
        else:
            reply_data = welcome_data
        get_started = {
            "get_started": {
                "payload": "get_started"
            },
            "greeting": [
                {
                    "locale": "default",
                    "text": reply_data
                }
            ]
        }
        our_page = Page(page_token, api_version=config('FB_API_VERSION'))
        our_page.set_get_started(get_started)

        # return page list
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facebookpages')
        rows = cursor.fetchall()

        # Convert query to objects of key-value pairs
        objects_list = []
        for row in rows:
            objects_list.append(
                {"uid": row[1], "avatar": row[2], "name": row[3], "selected": row[4]})

        data = objects_list
        conn.close()

        return jsonify(data)

    def delete(self):
        # clean page & reset page token
        FacebookPage.query.delete()
        self.user.u_token = None
        self.user.p_id = None
        self.user.p_token = None
        db.session.commit()
        self.token.unregister_app()
        return jsonify([])

# Upload
class UploadView(MethodView):
    def post(self):
        if 'files[0]' not in request.files:
            return jsonify(title="Fail! ", message="Tải lên không thành công", status="danger")

        for i in range(len(request.files)):
            fileStorageObj = request.files['files['+str(i)+']']
            if allowed_file(fileStorageObj.filename):
                filename = secure_filename(fileStorageObj.filename)
                data_asset = Asset.query.filter_by(a_key=filename).first()
                if not data_asset:
                    # save file
                    if '.csv' not in filename:
                        fileStorageObj.save(os.path.join(
                            app.config['UPLOAD_MEDIA'], filename))
                    else:
                        fileStorageObj.save(os.path.join(
                            app.config['UPLOAD_FILE'], filename))
                    # save to DB
                    self.a_key = filename
                    self.a_val = None
                    content = Asset(self.a_key, self.a_val)
                    db.session.add(content)
                    db.session.commit()

        # send data back to client
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM assets')
        rows = cursor.fetchall()

        # Convert query to objects of key-value pairs
        objects_list = []
        for row in rows:
            objects_list.append({"id": row[0], "key": row[1], "val": row[2]})

        data = objects_list
        conn.close()

        return jsonify(title="Success! ", message="Tải lên thành công", status="success", data=data)

# Download
class DownloadView(MethodView):
    def get(self, id):
        if id:
            conn = db_connect()
            cursor = conn.cursor()
            filename = id + '.csv'
            path = os.path.join(
                app.config['DOWNLOAD_FILE'], filename)
            sql = "COPY (SELECT uid,triggered FROM customers) TO STDOUT WITH CSV HEADER"
            with open(path, "w") as file:
                cursor.copy_expert(sql, file)
            conn.close()
            return send_file(path, mimetype='text/csv', attachment_filename=filename, as_attachment=True)
        else:
            abort(405)


# Connect to Database
def db_connect():
    conn_string = "host="+config('DB_HOST')+" dbname="+config(
        'DB_NAME')+" user="+config('DB_USERNAME')+" password="+config('DB_PASS')
    conn = psycopg2.connect(conn_string)
    return conn

# Allow files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
