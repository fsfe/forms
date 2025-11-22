"""Configuration parameters"""

# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from os import environ

# Parameters for Flask-Limiter
RATELIMIT_DEFAULT = environ.get("RATELIMIT_DEFAULT")

# Parameters for sending out all kinds of emails
MAIL_SERVER = environ.get("MAIL_SERVER", "localhost")
MAIL_HELO_HOST = environ.get("MAIL_HELO_HOST")  # None = let smtplib decide
MAIL_PORT: int = int(environ.get("MAIL_PORT", "25"))
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")

# Parameters for forwarding log messages by email
LOG_EMAIL_FROM = environ.get("LOG_EMAIL_FROM")
LOG_EMAIL_TO = environ.get("LOG_EMAIL_TO")

# Parameters for the connection to the Redis server
REDIS_HOST = environ.get("REDIS_HOST", "forms-redis")
REDIS_PORT: int = int(environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = environ.get("REDIS_PASSWORD", None)
REDIS_QUEUE_DB: int = int(environ.get("REDIS_QUEUE_DB", "0"))

# Parameters for the connection to the FSFE Community Database
FSFE_CD_URL = environ.get("FSFE_CD_URL", "http://localhost:8089/")
FSFE_CD_TIMEOUT: int = int(environ.get("FSFE_CD_TIMEOUT", "3"))
FSFE_CD_PASSPHRASE = environ.get("FSFE_CD_PASSPHRASE", "cmd_passphrase")

# Parameters for file operations
LOCK_FILENAME = environ.get("LOCK_FILENAME", "/tmp/forms.lock")
STORE_FILE_PREFIX = environ.get("STORE_FILE_PREFIX", "")

# Expiration time for double opt-in confirmation
# (None means no expiration)
CONFIRMATION_EXPIRATION_SECS: int = 86400

# Parameters for email address validation
VALIDATE_EMAIL_HELO = environ.get("VALIDATE_EMAIL_HELO", "localhost")
VALIDATE_EMAIL_FROM = environ.get("VALIDATE_EMAIL_FROM")

# Parameters for Token authentication, e.g. for API endpoints
TOKEN_FILE = environ.get("TOKEN_FILE")
