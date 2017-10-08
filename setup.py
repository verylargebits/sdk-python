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

import os
from setuptools import setup

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "verylargebits_sdk",
    packages = ["verylargebits_sdk"],
    version = "0.1.3",
    description = "Python SDK for the Very Large Bits API",
    long_description="\n\n".join([
        open(os.path.join(base_dir, "README.md"), "r").read(),
    ]),
    url = "https://github.com/verylargebits/sdk-python",
    download_url = "https://github.com/verylargebits/sdk-python/archive/0.1.3.tar.gz",
    author = "John Wells",
    author_email = "john@verylargebits.com",
    maintainer = "John Wells",
    maintainer_email = "john@verylargebits.com",
    classifiers=[
        # See: https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe = False,
    install_requires = ["requests"],
    tests_require = ["unittest2"],
    test_suite = "tests.all_tests",
)