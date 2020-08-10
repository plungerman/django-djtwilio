"""
Django settings for project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from djimix.settings.local import DBSERVERNAME
from djimix.settings.local import INFORMIX_ODBC
from djimix.settings.local import INFORMIX_ODBC_TRAIN
from djimix.settings.local import INFORMIXDIR
from djimix.settings.local import INFORMIXSERVER
from djimix.settings.local import INFORMIXSQLHOSTS
from djimix.settings.local import LD_LIBRARY_PATH
from djimix.settings.local import LD_RUN_PATH
from djimix.settings.local import MSSQL_EARL
from djimix.settings.local import ODBCINI
from djimix.settings.local import ONCONFIG

from djzbar.settings import INFORMIX_EARL_TEST as INFORMIX_EARL

# Debug
DEBUG = False
INFORMIX_DEBUG = 'debug'
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

SECRET_KEY = ''
ENCRYPTION_KEY = None

ALLOWED_HOSTS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = True
DEFAULT_CHARSET = 'utf8'
FILE_CHARSET = 'utf8'
SERVER_URL = ''
API_URL = '{}/{}'.format(SERVER_URL, 'api')
LIVEWHALE_API_URL = 'https://{}'.format(SERVER_URL)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(__file__)
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATIC_URL = '/static/djtwilio/'
ROOT_URL = '/apps/twilio'
MEDIA_ROOT = '{}/assets/'.format(BASE_DIR)
STATIC_ROOT = '{}/static/'.format(BASE_DIR)
MEDIA_URL = '{}assets/'.format(STATIC_URL)
UPLOADS_DIR = '{}files/'.format(MEDIA_ROOT)
UPLOADS_URL = '{}files/'.format(MEDIA_URL)
ROOT_URLCONF = 'djtwilio.core.urls'
WSGI_APPLICATION = 'djtwilio.wsgi.application'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_djtwilio',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': ''
    },
}
INSTALLED_APPS = [
    #'bootstrap_admin',
    'bootstrap4',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'djtwilio.core',
    'djtwilio.apps.sms',
    # needed for template tags
    'djtools',
    'loginas',
]
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # the following should be uncommented unless you are
    # embedding your apps in iframes
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            '/data2/django_templates/djbootmin/',
            '/data2/django_templates/django-djskins/',
            '/data2/django_templates/djcher/',
            '/data2/livewhale/includes/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    # insert your TEMPLATE_LOADERS here
            #]
        },
    },
]
# caching
'''
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        #'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        #'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        #'LOCATION': '/var/tmp/django_djtwilio_cache',
        #'TIMEOUT': 60*20,
        #'KEY_PREFIX': 'DJTWILIO_',
        #'OPTIONS': {
        #    'MAX_ENTRIES': 80000,
        #}
    }
}
'''
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
# LDAP Constants
LDAP_SERVER = ''
LDAP_SERVER_PWM = ''
LDAP_PORT = ''
LDAP_PORT_PWM = ''
LDAP_PROTOCOL = ''
LDAP_PROTOCOL_PWM = ''
LDAP_BASE = ''
LDAP_USER = ''
LDAP_PASS = ''
LDAP_EMAIL_DOMAIN = ''
LDAP_OBJECT_CLASS = ''
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_RETURN_PWM = []
LDAP_ID_ATTR = ''
LDAP_CHALLENGE_ATTR = ''
LDAP_AUTH_USER_PK = False
# auth backends
AUTHENTICATION_BACKENDS = (
    'djauth.ldapBackend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LOGIN_URL = '{}/accounts/login/'.format(ROOT_URL)
LOGOUT_URL = '{}/accounts/logout/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL
USE_X_FORWARDED_HOST = True
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN='.carthage.edu'
SESSION_COOKIE_NAME ='django_djtwilio_cookie'
SESSION_COOKIE_AGE = 1209600 # default, two weeks
# SMTP settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = False
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL=''
# bootstrap admin
BOOTSTRAP_ADMIN_SIDEBAR_MENU = True
# bootstrap forms
BOOTSTRAP4 = {
    'required_css_class': 'required',
}
# Twilio
TWILIO_API_URL = 'https://api.twilio.com/2010-04-01/'
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_FORGERY_PROTECTION = True
TWILIO_DEFAULT_FORWARD_PHONE=''
# redpanda constants
REDPANDA_SENDER_ID = 54
REDPANDA_TEST_CIDS = ()
REDPANDA_SERVER_URL = ''
REDPANDA_ROOT_URL = ''
REDPANDA_SHORT_URL_API = ''
# tests
TWILIO_TEST_BULK_NAME=''
TWILIO_TEST_BULK_DESCRIPTION=''
TWILIO_TEST_BULK_SENDER_ID=0
TWILIO_TEST_COLLEGE_ID=0
TWILIO_TEST_PHONE_TO = ''
TWILIO_TEST_PHONE_OPT_OUT = ''
TWILIO_TEST_MESSAGE = 'Who does your taxes?'
TWILIO_TEST_MESSAGE_SID = ''
TWILIO_TEST_DEPARTMENT = 'Admissions'
TWILIO_TEST_STATUS_DICT = {}
TWILIO_TEST_SENDER_ID=0
TWILIO_TEST_MESSAGING_SERVICE_SID_INVALID = ''
TWILIO_GROUP = 'Twilio Manager'
TWILIO_ADDMISSIONS_GROUP = 'Admissions SMS'
TWILIO_ADMISSIONS_REPS = {}
# auth tests
TEST_USERNAME = ''
TEST_PASSWORD = ''
TEST_EMAIL = ''
TEST_USER_ID = ''
# logging
LOG_FILEPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs/'
)
LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'debug.log')
DEBUG_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'debug.log')
INFO_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'info.log')
ERROR_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'error.log')
CUSTOM_LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'custom.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILENAME,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'custom_logfile': {
            'level':'ERROR',
            'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': CUSTOM_LOG_FILENAME,
            'formatter': 'custom',
        },
        'info_logfile': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'backupCount': 10,
            'maxBytes': 50000,
            'filters': ['require_debug_false'], # run logger in production
            'filename': INFO_LOG_FILENAME,
            'formatter': 'simple',
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILENAME,
            'formatter': 'verbose'
        },
        'error_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILENAME,
            'formatter': 'verbose'
        },
        'djtwilio': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'djtwilio.apps.sms': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'djtwilio.core': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
