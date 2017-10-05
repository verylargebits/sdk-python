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
import sys

try:
    import requests
except ImportError:
    raise ImportError('"requests" package not found: see requirements.txt')

"""This sample program (assets.py) demonstrates how to upload and check
the status of asset files using the Very Large Bits SDK for Python."""

def calc_sha1(filename):
    """Calculates and returns the base64 encoded SHA1 hash of a file"""

    sha1 = hashlib.sha1()

    with open(filename, 'rb') as file_:
        while True:
            data = file_.read(2 ** 16)
            if not data:
                break

            sha1.update(data)

    return base64.b64encode(sha1.digest(), b'-_').decode("utf-8")

def convert_byte_sz_str_to_int(value):
    """Takes a human-readble byte size string and returns the long form"""

    # Coerce the incoming value to a string
    if isinstance(value, int):
        value = str(value)

    value = value.upper()
    if value.endswith('MB'):
        return int(value[:-2]) * 1024 * 1024
    elif value.endswith('KB'):
        return int(value[:-2]) * 1024
    else:
        return int(value)

def print_help():
    """Prints out the details of command line usage of this program"""

    print("""Usage: python assets.py [OPTION]... [FILE]...')
Adds asset FILEs to the Very Large Bits system. Examples:
    python main.py movie.mp4
    python main.py -v movie.mp4
    python main.py --patch-size 24000000 movie.mp4
    python main.py --patch-size 24MB movie.mp4
    python main.py --key 0gjv9kpbct9w68809r6jh5ppgb --secret mykeyfile.pkcs8 movie.mp4

Also blocks until a specific status is reached. Example:
    python main.py -s USABLE movie.mp4

Security OPTIONs when using API key authentication:
    -k or --key       Override the config.json api-key value.
    -s or --secret    Override the config.json private-key-filename value.

Security OPTIONs when using basic API authentication:
    -e or --email    The email address used to sign in to dashboard.verylargebits.com.
    -p or --password Required if email is specificied.

Data OPTIONS:
    --patch-size      Override the default config.json patch-size value (default 4MB).

Other OPTIONs:
    -h or --help      Print this message.
    --status          Checks the status if none provided or waits until the
                      provided status is reached. Only valid value is USABLE.
    -w or --wait      The number of seconds to wait if a status value is provided
                      with -s. Default is 600 (10 minutes).
    -v or --verbose   Enable detailed output.""")
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
        # Fallback to defaults
        data = {}
        data['patch-size'] = '4MB'

    # Allow for specification of patch size in json
    if '--patch-size' in sys.argv:
        data['patch-size'] = sys.argv[sys.argv.index('--patch-size') + 1]

    # Allow for MB/KB suffixes to make patch size easier to understand
    data['patch-size'] = convert_byte_sz_str_to_int(data['patch-size'])

    # Allow for API key or email override
    if '-k' in sys.argv:
        data['api-key'] = sys.argv[sys.argv.index('-k') + 1]
        data['email'] = None
    elif '--key' in sys.argv:
        data['api-key'] = sys.argv[sys.argv.index('--key') + 1]
        data['email'] = None
    elif '-e' in sys.argv:
        data['api-key'] = None
        data['email'] = sys.argv[sys.argv.index('-e') + 1]
    elif '--email' in sys.argv:
        data['api-key'] = None
        data['email'] = sys.argv[sys.argv.index('--email') + 1]

    # Allow for API private key or password override
    if '-s' in sys.argv:
        data['email'] = None
        data['private-key-filename'] = sys.argv[sys.argv.index('-s') + 1]
    elif '--secret' in sys.argv:
        data['email'] = None
        data['private-key-filename'] = sys.argv[sys.argv.index('--secret') + 1]
    elif '-p' in sys.argv:
        data['api-key'] = None
        data['password'] = sys.argv[sys.argv.index('-p') + 1]
    elif '--password' in sys.argv:
        data['api-key'] = None
        data['password'] = sys.argv[sys.argv.index('--password') + 1]

    # Verbosity increases with any of the proper switches
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    if verbose:
        if 'api-key' in data and 'private-key-filename' in data:
            print('API key: %s' % data['api-key'])
            print('Private key: %s' % data['private-key-filename'])
        elif 'email' in data and 'password' in data:
            print('Email: %s' % data['email'])
            print('Password: %s' % ("*" * len(data['password'])))
        else:
            print_help()

        print('Patch size: %s bytes' % data['patch-size'])

    # Allow for changing the default 10 minute wait time for status checks
    wait_secs = 600
    if '-w' in sys.argv:
        wait_secs = int(sys.argv[sys.argv.index('-w') + 1])
    elif '--wait' in sys.argv:
        wait_secs = int(sys.argv[sys.argv.index('--wait') + 1])

    # The file should be the last argument
    filename = sys.argv[len(sys.argv) - 1]
    if verbose:
        print('File: %s' % filename)

    # All operations will require the URL-safe base64 encoded SHA1 file hash
    sha1 = calc_sha1(filename)
    if verbose:
        print('Hash: %s' % sha1)

    # Main logic: Do we check a status or upload?
    if '--status' in sys.argv and sys.argv[sys.argv.index('--status') + 1].upper() != 'USABLE':
        # We should check the status of the given file
        pass
    else:
        # We should upload the given file
        pass

main()
