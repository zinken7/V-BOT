import os
import json
import requests

from app.pymessenger import utils

DEFAULT_API_VERSION = 8.0


class Page:
    def __init__(self, access_token, **kwargs):
        """
            @required:
                access_token
            @optional:
                api_version
        """

        self.api_version = kwargs.get('api_version') or DEFAULT_API_VERSION
        self.app_secret = kwargs.get('app_secret')
        self.graph_url = 'https://graph.facebook.com/v{0}'.format(
            self.api_version)
        self.access_token = access_token

    @property
    def auth_args(self):
        if not hasattr(self, '_auth_args'):
            auth = {
                'access_token': self.access_token
            }
            if self.app_secret is not None:
                appsecret_proof = utils.generate_appsecret_proof(
                    self.access_token, self.app_secret)
                auth['appsecret_proof'] = appsecret_proof
            self._auth_args = auth
        return self._auth_args

    def page_like_comment(self, comment_id):
        """
        https://developers.facebook.com/docs/graph-api/reference/v9.0/object/likes
        """
        request_endpoint = '{0}/{1}/likes'.format(self.graph_url, comment_id)
        response = requests.post(
            request_endpoint,
            params=self.auth_args
        )
        result = response.json()
        return result

    def page_hide_comment(self, comment_id):
        """
        https://developers.facebook.com/docs/graph-api/reference/v9.0/comment
        """
        request_endpoint = '{0}/{1}'.format(self.graph_url, comment_id)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json={"is_hidden": True}
        )
        result = response.json()
        return result

    def page_reply_comment(self, comment_id, message):
        """
        https://developers.facebook.com/docs/graph-api/reference/v9.0/object/comments
        """
        request_endpoint = '{0}/{1}/comments'.format(
            self.graph_url, comment_id)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json={"message": message}
        )
        result = response.json()
        return result

    def send_message(self, comment_id, message):
        payload = {
            "recipient": {
                "comment_id": comment_id
            },
            "message": {
                "text": message
            },
            "message_type": "RESPONSE"
        }
        return self.send_raw(payload)

    def send_raw(self, payload):
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        result = response.json()
        return result
    
    def upload_file(self, image_url, file_type='image'):
        payload = {
            'message': {
                'attachment': {
                    'type': file_type,
                    'payload': {
                        "is_reusable": True,
                        "url": image_url
                    }
                }
            }
        }
        return self.upload_raw(payload)

    def upload_raw(self, payload):
        request_endpoint = '{0}/me/message_attachments'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params=self.auth_args,
            json=payload
        )
        result = response.json()
        return result

    def set_get_started(self, gs_obj):
        """Set a get started button shown on welcome screen for first time users
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/get-started-button
        Input:
          gs_obj: Your formatted get_started object as described by the API docs
        Output:
          Response from API as <dict>
        """
        request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params = self.auth_args,
            json = gs_obj
        )
        result = response.json()
        return result

    def set_persistent_menu(self, pm_obj):
        """Set a persistent_menu that stays same for every user. Before you can use this, make sure to have set a get started button.
        https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/persistent-menu
        Input:
          pm_obj: Your formatted persistent menu object as described by the API docs
        Output:
          Response from API as <dict>
        """
        request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params = self.auth_args,
            json = pm_obj
        )
        result = response.json()
        return result

    def remove_get_started(self):
            """delete get started button.
            https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/#delete
            Output:
            Response from API as <dict>
            """
            delete_obj = {"fields": ["get_started"]}
            request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
            response = requests.delete(
                request_endpoint,
                params = self.auth_args,
                json = delete_obj
            )
            result = response.json()
            return result

    def remove_persistent_menu(self):
            """delete persistent menu.
            https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/#delete
            Output:
            Response from API as <dict>
            """
            delete_obj = {"fields": ["persistent_menu"]}
            request_endpoint = '{0}/me/messenger_profile'.format(self.graph_url)
            response = requests.delete(
                request_endpoint,
                params = self.auth_args,
                json = delete_obj
            )
            result = response.json()
            return result
