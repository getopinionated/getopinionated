#!/usr/bin/env python
# Django settings for getopinionated project.
import sys, os
from os.path import dirname

SITE_ROOT = dirname(dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(SITE_ROOT, 'libs'))

#####################################################################################
# Django settings
#####################################################################################
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Brussels'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://localhost:8000/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, 'tmp/static')#Override this on your server

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'static'),
    os.path.join(SITE_ROOT, 'libs/debug_toolbar/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'common.middleware.SSLRedirect',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = 'getopinionated.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'getopinionated.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(SITE_ROOT, 'templates'),
    os.path.join(SITE_ROOT, 'libs/debug_toolbar/templates')
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
    'common.context_processors.add_settings_to_context'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.redirects',
    'django.contrib.flatpages',
    'common',
	'proposing',
    'document',
    'django.contrib.humanize',
    'accounts',
    'social_auth',
    # 'event', # temporarily disabled because not yet used
    # libs
    'libs.sorl.thumbnail',
    'libs.debug_toolbar',
    'libs.bootstrap_toolkit',
    # main app
    'getopinionated',
)
ENABLE_SOUTH = False

AUTHENTICATION_BACKENDS = (
    'accounts.backend.EmailModelBackend',
    'accounts.backend.CustomUserModelBackend',
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'accounts.eid.EIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# used by CustomUserModelBackend
CUSTOM_USER_MODEL = 'accounts.CustomUser'

### SSL settings (common.middleware.SSLRedirect) ###
# Forced SSL
SSL_URLS = (
    r'^/admin/',
    r'^/accounts/',
	r'.*',
)
# May be SSL & not SSL
MIXED_URLS = (
)

# The logging configuration.
# See http://docs.djangoproject.com/en/dev/topics/logging
# Sample usage:
#     import logging
#     logger = logging.getLogger(__name__)
#     logger.error('Something went wrong!')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_format': {
            'format': '[%(levelname)s in %(module)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console_format',
        },
        'mail_admins': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'proposing': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
        },
        'event': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
        },
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         #'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         #'LOCATION': '127.0.0.1:11211',
#     }
# }

# default url after login (used in contrib.auth)
LOGIN_REDIRECT_URL = '/'

#####################################################################################
# Mail settings
#####################################################################################

# favour django-mailer but fall back to django.core.mail
if "mailer" in INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

MAILER_LOCKFILE = os.path.join(SITE_ROOT, 'send_mail.lock')
MAILER_PAUSE_SEND = False

#####################################################################################
# Debug toobar settings
#####################################################################################
ENABLE_DJDT = False

if ENABLE_DJDT:
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

    def custom_show_toolbar(request):
        return True  # Always show toolbar, for example purposes only.

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'EXTRA_SIGNALS': [],
        'HIDE_DJANGO_SQL': False,
        'TAG': 'body',
        'ENABLE_STACKTRACES' : True,
    }

    INTERNAL_IPS = ('127.0.0.1',)

#####################################################################################
# Social auth settings
#####################################################################################

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.user.update_user_details',
    'accounts.pipelines.get_user_avatar',
)

TWITTER_CONSUMER_KEY         = ''
TWITTER_CONSUMER_SECRET      = ''
FACEBOOK_APP_ID              = ''
FACEBOOK_API_SECRET          = ''
LINKEDIN_CONSUMER_KEY        = ''
LINKEDIN_CONSUMER_SECRET     = ''
GOOGLE_OAUTH2_CLIENT_ID      = ''
GOOGLE_OAUTH2_CLIENT_SECRET  = ''

E_ID_OPENID_URL = 'https://www.e-contract.be/eid-idp/endpoints/openid/auth'

LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGIN_ERROR_URL    = '/accounts/login-error/'


#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/another-login-url/'

#SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
#SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
#SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/accounts/new-error-url/'
#SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
#SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

#TODO: fix if needed?
SOCIAL_AUTH_USER_MODEL = 'accounts.CustomUser'
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_UUID_LENGTH = 4 #random characters added when username already exists
SOCIAL_AUTH_SESSION_EXPIRATION = False

SOCIAL_AUTH_FORCE_POST_DISCONNECT = True


#####################################################################################
# Social feed settings
#####################################################################################
FEED_TWITTER_CONSUMER_KEY = ""
FEED_TWITTER_CONSUMER_SECRET = ""
FEED_TWITTER_ACCESS_TOKEN = "-"
FEED_TWITTER_ACCESS_SECRET = ""

#####################################################################################
# GetOpinionated-specific default settings
#####################################################################################

## project-specific content settings
DOMAIN_NAME = "http://www.foo.bar"
ORGANISATION_NAME = 'The Voting Organisation'
ABOUT_PAGE_FILENAME = 'about_page_default.html' # make sure this file exists in templates/about/
DEFAULT_DOCUMENT_SLUG = 'default-document' # url-friendly name of default document
DEFAULT_DOCUMENT_DESCRIPTION = 'Party Programme'
DEFAULT_DOCUMENT_DESCRIPTION_LONG = 'Party Programme of our organisation'
NEW_POSITION_LABEL = 'Propose a new position' # label of the button for proposing a new position
PROPOSAL_DESCRIPTION = '''Join the discussion and vote. Get opinionated! Everybody is free to step in and join the democratic
                          process of our organisation. Share your expertise and make our organisation better.'''
PROPOSAL_SHARE_DESCRIPTION = '''This interesting proposal for the Party Programme of our organisation has been made on getOpinionated. Help us make the program a better program.'''

## project-specific layout settings
SHOW_FOLLOW_US_ON_FB_AND_TWITTER_BANNER = False

## project-specific other settings
MEMBER_GROUP_NAME = 'member'

## anonymous user settings
ANONYMOUS_PROPOSALS = True # allow anonymous proposals if True
ANONYMOUS_COMMENTS = True # allow anonymous comments if True

COMMENTS_IN_DISCUSSION = True #
COMMENTS_IN_VOTING = True #
COMMENTS_IN_FINISHED = True #

## proposal settings
MIN_NUM_ENDORSEMENTS_BEFORE_VOTING = 3
QUORUM_SIZE = 1 # minimal # of proposalvotes for approvement
VOTING_DAYS = 7

## proposal type settings
## Note: These only disable the creation by users of these proposals, an administrator
##       can add them manually via the admin interface)
AMENDMENTS_ALLOWED = True # this defines as well whether the document system is used
POSITIONS_ALLOWED = True

## proxy settings
PROXIES_ALLOWED = True

## commentreply settings
COMMENTREPLY_MIN_LENGTH = 15
COMMENTREPLY_MAX_LENGTH = 500

## update settings
UNDER_MAINTENANCE = False

#####################################################################################
# Import local settings
#####################################################################################
try:
    from local_settings import *
except ImportError:
    try:
        from mod_python import apache
        apache.log_error("You need to copy local_settings.py.example to local_settings.py and edit settings")
    except ImportError:
        import sys
        sys.stderr.write("You need to copy local_settings.py.example to local_settings.py and edit settings")

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

if ENABLE_SOUTH:
    INSTALLED_APPS = INSTALLED_APPS + ('south',) # use south on online databases

# easier template debugging (http://stackoverflow.com/questions/4300442/show-undefined-variable-errors-in-templates)
if DEBUG:
    class InvalidString(str):
        def __mod__(self, other):
            # hack for bug in admin
            if str(other) == 'header.class_attrib':
                return
            from django.template.base import TemplateSyntaxError
            raise TemplateSyntaxError(
                "Undefined variable or unknown value for: \"%s\"" % other)
    TEMPLATE_STRING_IF_INVALID = InvalidString("%s")

# helps by logging to console
#import logging
#if DEBUG:
#    logging.basicConfig(
#        level = logging.INFO,
#        format = '%(asctime)s %(levelname)s %(message)s',
#    )
