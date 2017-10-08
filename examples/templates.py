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

def print_help():
    """Prints out the details of command line usage of this program"""

    print("""Usage: python templates.py [OPTION]...')
Adds and renders templates using the Very Large Bits system. Examples:
    python templates.py --template template.json
    python templates.py --render 6nnrqkpbffq8ke6y7rh6trccz5 --vars vars.json
    python templates.py --key fyn615m07rbpfmydvk3re6wwgq --secret c:\mykeyfile.pkcs8 --template template.json

Also blocks until a specific status is reached. Example:
    python templates.py -s DONE -r 6nnrqkpbffq8ke6y7rh6trccz5 -v vars.json

Security OPTIONs when using API Key authentication:
    -k or --key         Override the config.json api-key value.
    -s or --secret      Override the config.json private-key-filename value.

Security OPTIONs when using basic API authentication:
    -e or --email       The email address used to sign in to dashboard.verylargebits.com.
    -p or --password    Required if email is specificied.

Template OPTIONs:
    -t or --template    A JSON-formatted template file conforming to the Very Large Bits
                        standards.

Render OPTIONs:
  -r or --render        The ID of the template to render with variable replacements or
                        the ID of the render to check or wait upon for status. If this value
                        is a file then it must be a JSON-formatted template file.
  --vars                A JSON-formatted dictionary file which specifies
                        variable-replacement operations, if any.
  --status              Checks the status if none provided or waits until the
                        provided status is reached. Only valid value is DONE.
  -w or --wait          The number of seconds to wait if a status value is provided with
                        --status. Default is 600 (10 minutes).

Other OPTIONs:
  -h or --help          Print this message.  
  -v or --verbose       Enable detailed output.""")
    sys.exit()
