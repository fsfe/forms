import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 25))

CONFIRMATION_EMAIL_SUBJECT = 'Confirm your email'
CONFIRMATION_EXPIRATION_SECS = 86400  # You can set None if you don't want to have expiration of emails confirmation
