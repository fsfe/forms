import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 25))

LOCK_FILENAME = os.environ.get('LOCK_FILENAME', '/tmp/forms.lock')

CONFIRMATION_EMAIL_SUBJECT = 'Confirm your email'
CONFIRMATION_DUPLICATE_EMAIL_SUBJECT = 'Confirmation duplicate email'
CONFIRMATION_EXPIRATION_SECS = 86400  # You can set None if you don't want to have expiration of emails confirmation

DEFAULT_SUBJECT_LANG = 'en'
LANG_STRING_TOKEN = '{lang}'
CONFIRMATION_MULTILANG_TEMPLATE = f'common/templates/confirmation.{LANG_STRING_TOKEN}.html'
CONFIRMATION_DUPLICATE_MULTILANG_TEMPLATE = f'common/templates/confirmation_duplicate.{LANG_STRING_TOKEN}.html'
