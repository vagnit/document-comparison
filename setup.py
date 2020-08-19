#! /usr/bin/env python
"""Tools to extract and compare documents for EMA."""

import codecs
import os

from setuptools import find_packages, setup

ver_file = os.path.join('docomp', '_version.py')
with open(ver_file) as f:
    exec(f.read())

DISTNAME = 'document-comparison'
DESCRIPTION = 'Tools to extract and compare documents for EMA.'
with codecs.open('README.rst', encoding='utf-8-sig') as f:
    LONG_DESCRIPTION = f.read()
URL = 'https://github.com/georgedouzas/document-comparison.git'
DOWNLOAD_URL = 'https://github.com/georgedouzas/document-comparison.git'
VERSION = __version__
INSTALL_REQUIRES = ['pandas>=1.1.0', 'xlrd>=1.0.0', 'beautifulsoup4>=4.9.1']
CLASSIFIERS = ['Intended Audience :: Developers',
               'Programming Language :: Python',
               'Topic :: Software Development',
               'Topic :: Scientific/Engineering',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: POSIX',
               'Operating System :: Unix',
               'Operating System :: MacOS',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               'Programming Language :: Python :: 3.8']
EXTRAS_REQUIRE = {
    'tests': [
        'pytest',
        'pytest-cov'],
}

setup(
    name=DISTNAME,
    description=DESCRIPTION,
    url=URL,
    version=VERSION,
    download_url=DOWNLOAD_URL,
    long_description=LONG_DESCRIPTION,
    zip_safe=False,
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE
)
