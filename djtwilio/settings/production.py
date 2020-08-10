from .local import *

from djzbar.settings import INFORMIX_EARL_PROD as INFORMIX_EARL

ALLOWED_HOSTS =  [
    'localhost','127.0.0.1','ceres.carthage.edu','www.carthage.edu'
]
DEBUG = False
#DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
ROOT_URL = '/apps/twilio'
TWILIO_API_URL = 'https://api.twilio.com/2010-04-01/'
LOGIN_REDIRECT_URL = ROOT_URL
