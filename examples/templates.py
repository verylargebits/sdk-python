#!/usr/bin/env python
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

from __future__ import print_function
import base64
import hashlib
import json
import math
from os.path import getsize
import sys

# Python hack to allow for our folder structure
from sys import path
from os.path import dirname
path.append(dirname(path[0]))
import src
# End hack

from src.client import Client

"""This sample program (templates.py) demonstrates how to add and render
video templates using the Very Large Bits SDK for Python."""

# Configuration file keys and defaults
API_KEY = 'api-key'
EMAIL = 'email'
PASSWORD = 'password'
PRIVATE_KEY = 'private-key-filename'

def print_help():
    """Prints out the details of command line usage of this program"""

    print("""Usage: python templates.py [OPTION]...')
Adds and renders templates using the Very Large Bits system. Examples:
    python templates.py --template template.json
    python templates.py --render 6nnrqkpbffq8ke6y7rh6trccz5 --vars vars.json
    python templates.py --key fyn615m07rbpfmydvk3re6wwgq --secret mykeyfile.pkcs8 --template template.json

Also blocks until a specific status is reached. Example:
    python templates.py --status DONE -r 6nnrqkpbffq8ke6y7rh6trccz5 --vars vars.json

Security OPTIONs when using API Key authentication:
    -k or --key         Override the config.json api-key value.
    -s or --secret      Override the config.json private-key-filename value.

Security OPTIONs when using basic API authentication:
    -e or --email       The email address used to sign in to dashboard.verylargebits.com.
    -p or --password    Required if email is specificied.

Template OPTIONs:
    -t or --template    A JSON-formatted template file conforming to the Very Large Bits
                        standards to upload.

Render OPTIONs:
    -r or --render      The ID of the template to render with variable replacements or
                        the ID of the render to check or wait upon for status. If this value
                        is a file then it must be a JSON-formatted template file.
    --vars              A JSON-formatted dictionary file which specifies
                        variable-replacement operations, if any.
    --status            Checks the status if none provided or waits until the
                        provided status is reached. Only valid value is DONE.
    -w or --wait        The number of seconds to wait if a status value is provided with
                        --status. Default is 600 (10 minutes).

Other OPTIONs:
    -h or --help        Print this message.  
    -v or --verbose     Enable detailed output.""")
    sys.exit()

def main():
    """Entry point for assets sample program."""

    # Provide some help if asked
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()

    # Try to open the config.json file
    try:
        with open('config.json') as config_file:
            data = json.load(config_file)
    except (OSError, IOError):
        data = {}

    # Allow for API key or email override
    if '-k' in sys.argv:
        data[API_KEY] = sys.argv[sys.argv.index('-k') + 1]
        data[EMAIL] = None
    elif '--key' in sys.argv:
        data[API_KEY] = sys.argv[sys.argv.index('--key') + 1]
        data[EMAIL] = None
    elif '-e' in sys.argv:
        data[API_KEY] = None
        data[EMAIL] = sys.argv[sys.argv.index('-e') + 1]
    elif '--email' in sys.argv:
        data[API_KEY] = None
        data[EMAIL] = sys.argv[sys.argv.index('--email') + 1]

    # Allow for API private key or password override
    if '-s' in sys.argv:
        data[EMAIL] = None
        data[PRIVATE_KEY] = sys.argv[sys.argv.index('-s') + 1]
    elif '--secret' in sys.argv:
        data[EMAIL] = None
        data[PRIVATE_KEY] = sys.argv[sys.argv.index('--secret') + 1]
    elif '-p' in sys.argv:
        data[API_KEY] = None
        data[PASSWORD] = sys.argv[sys.argv.index('-p') + 1]
    elif '--password' in sys.argv:
        data[API_KEY] = None
        data[PASSWORD] = sys.argv[sys.argv.index('--password') + 1]

    # Verbosity increases with any of the proper switches
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    if verbose:
        if API_KEY in data and PRIVATE_KEY in data:
            print('API key: %s' % data[API_KEY])
            print('Private key: %s' % data[PRIVATE_KEY])
        elif EMAIL in data and PASSWORD in data:
            print('Email: %s' % data[EMAIL])
            print('Password: %s' % ("*" * len(data[PASSWORD])))
        else:
            print_help()

    # Create either a BASIC or SIGNATURE api client
    if API_KEY in data:
        client = Client.from_sig_auth(data[API_KEY], data[PRIVATE_KEY])
    else:
        client = Client.from_basic_auth(data[EMAIL], data[PASSWORD])

    # Main logic: Do we upload a template or submit a render request?
    if '-t' in sys.argv or '--template' in sys.argv:
        # We should upload a template json file
        if '-t' in sys.argv:
            filename = sys.argv[sys.argv.index('-t') + 1]
        else:
            filename = sys.argv[sys.argv.index('--template') + 1]

        # Open the template json file
        with open(filename) as template_file:
            template = json.load(template_file)

        resp = client.post_template(template)
        if resp.status_code == 200:
            resp = resp.json()
            print('Template: %s' % resp['id'])
        else:
            print('HTTP Error: %s' % resp)
    else:
        # We should submit a render request

        # Allow for changing the default 10 minute wait time for status checks
        wait_secs = 600
        if '-w' in sys.argv:
            wait_secs = int(sys.argv[sys.argv.index('-w') + 1])
        elif '--wait' in sys.argv:
            wait_secs = int(sys.argv[sys.argv.index('--wait') + 1])

main()