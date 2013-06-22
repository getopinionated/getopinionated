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

EMAIL_HOST = 'mail.infomaniak.ch'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'opinion@pirateparty.be'
EMAIL_HOST_PASSWORD = 'separate long shadow cloth'
EMAIL_USE_TLS = True

STATIC_ROOT = '/home/de317070/webapps/staticmedia/'
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')
MEDIA_URL = '/static/media/'

FACEBOOK_APP_ID              = '298186733641393'
FACEBOOK_API_SECRET          = 'a3e382a140420334f8d1b0889e54d906'
TWITTER_CONSUMER_KEY         = 'VHhSNhnksKqve3TWvXNYkw'
TWITTER_CONSUMER_SECRET      = 'paZBVU3s0IWKcEIDns0BqCMocgDsw2DhLt2zfdfS4'
LINKEDIN_CONSUMER_KEY        = 'qfofhn3zb6i1'
LINKEDIN_CONSUMER_SECRET     = 'ldgZcVY3nigDHqJQ'
GOOGLE_OAUTH2_CLIENT_ID      = '488855642374.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET  = 'A2VRZIrLs1Fxu3XosRv_K5RN'
