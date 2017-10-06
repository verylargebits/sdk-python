# coding: utf-8

"""Copyright(c) 2017, Very Large Bits LLC

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import base64
import json

try:
    import requests
except ImportError:
    raise ImportError('"requests" package not found: see requirements.txt')

# Configuration file keys and defaults
SERVICE_URL = 'service-url'
SERVICE_URL_DEFAULT = 'https://api.verylargebits.com'

class BasicAuthClient(object):
    """An authentication provider using the email and password method"""

    def __init__(self, email, password):
        self._email = email
        self._password = password

    def auth_value(self, url, verb, body):
        creds = self._email + ':' + self._password

        return 'Basic ' + base64.urlsafe_b64encode(creds.encode('utf-8')).decode('utf-8')

class Client(object):
    """REST Client for the Very Large Bits API"""

    def __init__(self):
        self.auth_impl = None

        # Try to open the config.json file
        try:
            with open('config.json') as config_file:
                self.data = json.load(config_file)
        except (OSError, IOError):
            # Fallback to defaults
            self.data = {}

        if SERVICE_URL not in self.data:
            self.data[SERVICE_URL] = SERVICE_URL_DEFAULT

    @classmethod
    def from_basic_auth(cls, email, password):
        client = Client()
        client.auth_impl = BasicAuthClient(email, password)

        return client

    @classmethod
    def from_sig_auth(cls, api_key, private_key_filename):
        client = Client()
        client.auth_impl = SignatureAuthClient(api_key, private_key_filename)

        return client

    def get_status(self, sha1):
        url = self.data[SERVICE_URL] + '/assets/' + sha1
        headers = {
            'Authorization': self.auth_impl.auth_value(url, 'GET', None),
        }

        return requests.get(url, headers=headers)

    def patch_asset(self, asset_id, patch_index, data):
        url = self.data[SERVICE_URL] + '/asset/' + asset_id + '/' + str(patch_index)
        headers = {
            'Authorization': self.auth_impl.auth_value(url, 'PATCH', data),
            'Content-Type': 'application/octet-stream',
        }

        return requests.patch(url, headers=headers, data=data)

    def post_asset(self, data, sha1, patch_count):
        url = self.data[SERVICE_URL] + '/asset'
        body = None
        if patch_count == 0:
            body = data
        else:
            body = {
                'data': base64.b64encode(data).decode('utf-8'),
                'hash': sha1,
                'patch_count': patch_count,
            }

        headers = {
            'Authorization': self.auth_impl.auth_value(url, 'POST', body),
        }

        if patch_count == 0:
            headers['Content-Type'] = 'application/octet-stream'
            return requests.post(url, headers=headers, data=body)
        else:
            headers['Content-Type'] = 'application/json'
            return requests.post(url, headers=headers, json=body)

class SignatureAuthClient(object):
    """An authentication provider using the RSA signature method"""

    def __init__(self, api_key, password):
        self._api_key = api_key
        self._password = password

    def auth_value(self, url, verb, body):
        return "Nothing"
