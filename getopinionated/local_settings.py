#!/usr/bin/env python
import sys, os
from os.path import dirname

SITE_ROOT = dirname(dirname(os.path.realpath(__file__)))

DEBUG = True
ADMINS = ()
DEVELOPMENT = True # disables SSL redirects

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': SITE_ROOT + '/database.sqlite3',     # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

