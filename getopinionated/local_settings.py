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

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = '<username>@gmail.com'
EMAIL_HOST_PASSWORD = '<gmail password>'
EMAIL_USE_TLS = True

FACEBOOK_APP_ID              = '298186733641393'
FACEBOOK_API_SECRET          = 'a3e382a140420334f8d1b0889e54d906'
