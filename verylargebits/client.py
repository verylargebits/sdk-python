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
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
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

    def auth_value(self, verb, url, body=None):
        """Returns the Authorization header value for the given arguments"""

        del verb, url, body
        creds = self._email + ':' + self._password

        return 'Basic ' + base64.urlsafe_b64encode(creds.encode('utf-8')).decode('utf-8')

class Client(object):
    """REST Client for the Very Large Bits API"""

    def __init__(self, service_url):
        self.auth_impl = None

        if service_url == None:
            # Try to open the config.json file
            try:
                with open('config.json') as config_file:
                    self.data = json.load(config_file)
            except (OSError, IOError):
                self.data = {}
        else:
            self.data = {}

        if service_url != None:
            self.data[SERVICE_URL] = service_url
        elif SERVICE_URL not in self.data:
            self.data[SERVICE_URL] = SERVICE_URL_DEFAULT

    @classmethod
    def from_basic_auth(cls, email, password, service_url=None):
        client = Client(service_url)
        client.auth_impl = BasicAuthClient(email, password)

        return client

    @classmethod
    def from_sig_auth(cls, api_key, private_key_filename, service_url=None):
        client = Client(service_url)
        client.auth_impl = SignatureAuthClient(api_key, private_key_filename)

        return client

    def get_asset_status(self, sha1):
        sub_url = '/assets/' + sha1
        full_url = self.data[SERVICE_URL] + sub_url
        headers = {
            'Authorization': self.auth_impl.auth_value('GET', sub_url, None),
        }

        return requests.get(full_url, headers=headers)

    def get_render_status(self, render_id):
        sub_url = '/render/' + render_id + '/status'
        full_url = self.data[SERVICE_URL] + sub_url
        headers = {
            'Authorization': self.auth_impl.auth_value('GET', sub_url, None),
        }

        return requests.get(full_url, headers=headers)

    def patch_asset(self, asset_id, patch_index, data):
        sub_url = '/asset/' + asset_id + '/' + str(patch_index)
        full_url = self.data[SERVICE_URL] + sub_url
        headers = {
            'Authorization': self.auth_impl.auth_value('PATCH', sub_url, data),
            'Content-Type': 'application/octet-stream',
        }

        return requests.patch(full_url, headers=headers, data=data)

    def post_asset(self, data, sha1=None, patch_count=0):
        sub_url = '/asset'
        full_url = self.data[SERVICE_URL] + sub_url
        body = None
        if patch_count == 0:
            body = data
        else:
            body = json.dumps({
                'data': base64.b64encode(data).decode('utf-8'),
                'hash': sha1,
                'patch_count': patch_count,
            }).encode('utf-8')

        headers = {
            'Authorization': self.auth_impl.auth_value('POST', sub_url, body),
        }

        if patch_count == 0:
            headers['Content-Type'] = 'application/octet-stream'
            return requests.post(full_url, headers=headers, data=body)
        else:
            headers['Content-Type'] = 'application/json'
            return requests.post(full_url, headers=headers, data=body)

    def post_render(self, template_id, vars_, wait_until, wait_for):
        sub_url = '/render'
        full_url = self.data[SERVICE_URL] + sub_url
        body = json.dumps({
            'src': template_id,
            'vars': vars_,
        })
        headers = {
            'Authorization': self.auth_impl.auth_value('POST', sub_url, body),
            'Content-Type': 'application/json',
        }

        if wait_until != None:
            headers['x-wait-until'] = wait_until
            headers['x-wait-for'] = str(wait_for)

        return requests.post(full_url, headers=headers, data=body)

    def post_template(self, template):
        sub_url = '/template'
        full_url = self.data[SERVICE_URL] + sub_url
        body = json.dumps(template)
        headers = {
            'Authorization': self.auth_impl.auth_value('POST', sub_url, body),
            'Content-Type': 'application/json',
        }

        return requests.post(full_url, headers=headers, data=body)

class SignatureAuthClient(object):
    """An authentication provider using the RSA signature method"""

    def __init__(self, api_key, private_key_filename):
        self._api_key = api_key
        self._private_key = RSA.importKey(open(private_key_filename, 'r').read())

    def auth_value(self, verb, url, body=None):
        """Returns the Authorization header value for the given arguments"""

        signer = PKCS1_v1_5.new(self._private_key)
        digest = SHA256.new()
        digest.update(verb.encode('utf-8'))
        digest.update(url.encode('utf-8'))

        if body != None:
            digest.update(body)

        signature = signer.sign(digest)
        sig = base64.b64encode(signature)

        return 'Signature ' + self._api_key + ':SHA256:' \
            + sig.decode('utf-8')
