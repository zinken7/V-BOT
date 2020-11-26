import os, json, requests

DEFAULT_API_VERSION = 8.0


class Token:
    def __init__(self, app_id, **kwargs):
        self.app_id = app_id
        self.user_id = kwargs.get('user_id')
        self.api_version = kwargs.get('api_version') or DEFAULT_API_VERSION
        self.app_secret = kwargs.get('app_secret')
        self.app_token = self.app_id+'|'+self.app_secret
        self.graph_url = 'https://graph.facebook.com/v{0}'.format(self.api_version)

    def get_ll_token(self, ushort_token):
        request_endpoint = '{0}/oauth/access_token'.format(self.graph_url)
        auth_pr = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': ushort_token
        }
        try_times = 0
        while try_times < 3:
            try:
                response = requests.get(
                    request_endpoint,
                    params=auth_pr
                )
                result = response.json()
                return result['access_token']
            except:
                try_times += 1
    
    def get_page(self, ulong_token):
        request_endpoint = '{0}/{1}/accounts'.format(self.graph_url, self.user_id)
        try_times = 0
        while try_times < 3:
            try:
                response = requests.get(
                    request_endpoint,
                    params={'fields': 'access_token,name,picture.height(999){url}', 'access_token': ulong_token}
                )
                result = response.json()
                return result['data']
            except:
                try_times += 1

    def get_page_token(self, ulong_token, page_id):
        request_endpoint = '{0}/{1}'.format(self.graph_url, page_id)
        try_times = 0
        while try_times < 3:
            try:
                response = requests.get(
                    request_endpoint,
                    params={'fields': 'access_token', 'access_token': ulong_token}
                )
                result = response.json()
                return result['access_token']
            except:
                try_times += 1

    def check_token(self, check_token, real_token):
        request_endpoint = '{0}/debug_token'.format(self.graph_url)
        auth_pr = {
            'input_token': check_token,
            'access_token': real_token
        }
        try_times = 0
        while try_times < 3:
            try:
                response = requests.get(
                    request_endpoint,
                    params=auth_pr
                )
                result = response.json()
                return result['data']['is_valid']
            except:
                try_times += 1

    def register_app_fields(self, callback_url, verify_token, app_fields):
        request_endpoint = '{0}/{1}/subscriptions'.format(self.graph_url, self.app_id)
        sub_param = {
            'access_token': self.app_token,
            'object': 'page',
            'callback_url': callback_url,
            'verify_token': verify_token,
            'fields': app_fields
        }
        response = requests.post(
            request_endpoint,
            params=sub_param
        )
        result = response.json()
        return result
    
    
    def unregister_app(self):
        request_endpoint = '{0}/{1}/subscriptions'.format(self.graph_url, self.app_id)
        sub_param = {
            'access_token': self.app_token,
            'object': 'page'
        }
        response = requests.delete(
            request_endpoint,
            params=sub_param
        )
        result = response.json()
        return result
