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
import json
import sys

# Python hack to allow for our folder structure
from sys import path
from os.path import dirname
path.append(dirname(path[0]))
import verylargebits
# End hack

from verylargebits.client import Client

"""This sample program (templates.py) demonstrates how to add and render
video templates using the Very Large Bits SDK for Python."""

# Configuration file keys and defaults
API_KEY = 'api-key'
EMAIL = 'email'
PASSWORD = 'password'
PRIVATE_KEY = 'private-key-filename'
SERVICE_URL = 'service-url'

def print_help():
    """Prints out the details of command line usage of this program"""

    print("""Usage: python templates.py [OPTION]...')
Adds templates using the Very Large Bits system. Examples:
    python templates.py --template template.json
    python templates.py --key fyn615m07rbpfmydvk3re6wwgq --secret mykeyfile.pkcs8 -t template.json

Renders templates using the Very Large Bits system. Examples:
    python templates.py --render 6nnrqkpbffq8ke6y7rh6trccz5 --vars vars.json
    python templates.py -r 6nnrqkpbffq8ke6y7rh6trccz5 --vars vars.json --done
    python templates.py -r 6nnrqkpbffq8ke6y7rh6trccz5 --store-http POST https://myserver/endpoint

Checks the status of existing renders using the Very Large Bits system. Example:
    python templates.py --status 6nnrqkpbffq8ke6y7rh6trccz5

Security OPTIONs when using API Key authentication:
    -k or --key         Override the config.json api-key value.
    -s or --secret      Override the config.json private-key-filename value.

Security OPTIONs when using basic API authentication:
    -e or --email       The email address used to sign in to dashboard.verylargebits.com.
    -p or --password    Required if email is specificied.

Template mode OPTIONs:
    -t or --template    A JSON-formatted template file conforming to the Very Large Bits
                        specification to upload. Returns the ID of the new template.

Render mode OPTIONs:
    -r or --render      The ID of the template to render. Returns the ID of the new render.
    --done              Blocks until rendering and storage operations have completed.
    --store-http        If specified must be followed by the HTTP method and endpoint.
    --vars              A JSON-formatted dictionary file which specifies variable-replacement
                        operations, if any.
    -w or --wait        The number of seconds to block when --done is used. Default is
                        600 (10 minutes).

Status mode OPTIONs:
    --status            The ID of the render to check the status of.

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
        data.pop(EMAIL, None)
    elif '--key' in sys.argv:
        data[API_KEY] = sys.argv[sys.argv.index('--key') + 1]
        data.pop(EMAIL, None)
    elif '-e' in sys.argv:
        data.pop(API_KEY, None)
        data[EMAIL] = sys.argv[sys.argv.index('-e') + 1]
    elif '--email' in sys.argv:
        data.pop(API_KEY, None)
        data[EMAIL] = sys.argv[sys.argv.index('--email') + 1]

    # Allow for API private key or password override
    if '-s' in sys.argv:
        data.pop(EMAIL, None)
        data[PRIVATE_KEY] = sys.argv[sys.argv.index('-s') + 1]
    elif '--secret' in sys.argv:
        data.pop(EMAIL, None)
        data[PRIVATE_KEY] = sys.argv[sys.argv.index('--secret') + 1]
    elif '-p' in sys.argv:
        data.pop(API_KEY, None)
        data[PASSWORD] = sys.argv[sys.argv.index('-p') + 1]
    elif '--password' in sys.argv:
        data.pop(API_KEY, None)
        data[PASSWORD] = sys.argv[sys.argv.index('--password') + 1]

    # Allow for changing the service url
    if SERVICE_URL not in data:
        data[SERVICE_URL] = None

    # Verbosity increases with any of the proper switches
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    if verbose:
        if API_KEY in data and PRIVATE_KEY in data:
            print('API key: %s' % data[API_KEY])
            print('Private key: %s' % data[PRIVATE_KEY])
        elif EMAIL in data and PASSWORD in data:
            print('Email: %s' % data[EMAIL])
            print('Password: %s' % ('*' * len(data[PASSWORD])))
        else:
            print_help()

    # Create either a BASIC or SIGNATURE api client
    if API_KEY in data:
        client = Client.from_sig_auth(data[API_KEY], data[PRIVATE_KEY], service_url=data[SERVICE_URL])
    else:
        client = Client.from_basic_auth(data[EMAIL], data[PASSWORD], service_url=data[SERVICE_URL])

    # Main logic: Do we upload a template or work with a render request?
    if '-t' in sys.argv or '--template' in sys.argv:
        # We should upload a template json file
        if '-t' in sys.argv:
            filename = sys.argv[sys.argv.index('-t') + 1]
        else:
            filename = sys.argv[sys.argv.index('--template') + 1]

        # Open the template json file
        with open(filename) as template_file:
            template = json.load(template_file)

        # Use the SDK to upload a new template
        resp = client.post_template(template)
        if resp.status_code == 200:
            print('Template: %s' % resp.json()['id'])
        else:
            print('HTTP Error: %s' % resp)
    elif '-r' in sys.argv or '--render' in sys.argv:
        # We should render an existing template
        if '-r' in sys.argv:
            template_id = sys.argv[sys.argv.index('-r') + 1]
        else:
            template_id = sys.argv[sys.argv.index('--render') + 1]

        # Optional wait-until status is reached
        if '--done' in sys.argv:
            wait_until = 'DONE'

            # Allow for changing the default 10 minute wait time for status checks
            if '-w' in sys.argv:
                wait_secs = int(sys.argv[sys.argv.index('-w') + 1])
            elif '--wait' in sys.argv:
                wait_secs = int(sys.argv[sys.argv.index('--wait') + 1])
            else:
                wait_secs = None
        else:
            wait_until = None
            wait_secs = None

        # Allow for HTTP storage
        if '--store-http' in sys.argv:
            storage = {
                'type': 'HTTP',
                'verb': sys.argv[sys.argv.index('--store-http') + 1],
                'url': sys.argv[sys.argv.index('--store-http') + 2],
            }
        else:
            storage = None

        # Load the vars dictionary file, if provided
        if '--vars' in sys.argv:
            with open(sys.argv[sys.argv.index('--vars') + 1]) as vars_file:
                vars_ = json.load(vars_file)
        else:
            vars_ = None

        # Use the SDK to render an existing template
        resp = client.post_render(template_id,
                                  storage=storage,
                                  vars_=vars_,
                                  wait_until=wait_until,
                                  wait_secs=wait_secs)
        if resp.status_code == 200:
            print('Render: %s' % resp.json()['id'])
        else:
            print('HTTP Error: %s' % resp)
    elif '--status' in sys.argv:
        # We should check the status of an existing render
        render_id = sys.argv[sys.argv.index('--status') + 1]

        # Use the SDK to check the status of an existing render
        resp = client.get_render_status(render_id)
        if resp.status_code == 200:
            print('Status: %s' % resp.json()['status'])
        else:
            print('HTTP Error: %s' % resp)
    else:
        print_help()

main()
