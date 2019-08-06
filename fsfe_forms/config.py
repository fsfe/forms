# =============================================================================
# Configuration parameters
# =============================================================================
# This file is part of the FSFE Form Server.
#
# Copyright © 2017-2019 Free Software Foundation Europe <contact@fsfe.org>
#
# The FSFE Form Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# The FSFE Form Server is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details <http://www.gnu.org/licenses/>.
# =============================================================================

from os import environ


# Parameters for Flask-Limiter
RATELIMIT_DEFAULT = environ.get('RATELIMIT_DEFAULT')

# Parameters for sending out all kinds of emails
MAIL_SERVER = environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(environ.get('MAIL_PORT', 25))
MAIL_USERNAME = environ.get('MAIL_USERNAME')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

# Parameters for forwarding log messages by email
LOG_EMAIL_FROM = environ.get('LOG_EMAIL_FROM')
LOG_EMAIL_TO = environ.get('LOG_EMAIL_TO')

# Parameters for the connection to the redis server
REDIS_HOST = environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = environ.get('REDIS_PASSWORD', None)
REDIS_QUEUE_DB = int(environ.get('REDIS_QUEUE_DB', 0))

# Filename for a temporary lockfile
LOCK_FILENAME = environ.get('LOCK_FILENAME', '/tmp/forms.lock')

# Expiration time for double opt-in confirmation
# (None means no expiration)
CONFIRMATION_EXPIRATION_SECS = 86400
