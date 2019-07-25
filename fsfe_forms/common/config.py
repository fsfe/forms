import os

RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT')

MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

LOG_EMAIL_FROM = os.environ.get('LOG_EMAIL_FROM')
LOG_EMAIL_TO = os.environ.get('LOG_EMAIL_TO')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

LOCK_FILENAME = os.environ.get('LOCK_FILENAME', '/tmp/forms.lock')

CONFIRMATION_EXPIRATION_SECS = 86400  # You can set None if you don't want to have expiration of emails confirmation

SENDER_TABLE = 'sender'
