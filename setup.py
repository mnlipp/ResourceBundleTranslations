import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ""

import rbtranslations

setup(
    name = "rbtranslations",
    version = rbtranslations.__version__,
    author = "Michael N. Lipp",
    author_email = "mnl@mnl.de",
    description = ("Java ResourceBundle like approach to localization."),
    license = "MIT",
    keywords = "ResourceBundle Translations i18n l10n internationalization",
    url = "http://packages.python.org/rbtranslations",
    packages=['tests'],
    package_data={'tests': ['*.properties']},
    long_description=read('pypi-overview.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Internationalization",
        "License :: OSI Approved :: MIT License",
    ],
    platforms='any',
    py_modules=['rbtranslations'],
)