# =============================================================================
# Configuration parameters
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import urllib.parse
from os import environ

from sqlalchemy import create_engine, URL


# Parameters for Flask-Limiter
RATELIMIT_DEFAULT = environ.get("RATELIMIT_DEFAULT")

# Parameters for sending out all kinds of emails
MAIL_SERVER = environ.get("MAIL_SERVER", "localhost")
MAIL_HELO_HOST = environ.get("MAIL_HELO_HOST")  # None = let smtplib decide
MAIL_PORT = int(environ.get("MAIL_PORT", 25))
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")

# Parameters for forwarding log messages by email
LOG_EMAIL_FROM = environ.get("LOG_EMAIL_FROM")
LOG_EMAIL_TO = environ.get("LOG_EMAIL_TO")

# Parameters for the connection to the Redis server
REDIS_HOST = environ.get("REDIS_HOST", "forms-redis")
REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = environ.get("REDIS_PASSWORD", None)
REDIS_QUEUE_DB = int(environ.get("REDIS_QUEUE_DB", 0))

# Parameters for the connection to the FSFE Community Database
FSFE_CD_URL = environ.get("FSFE_CD_URL", "http://localhost:8089/")
FSFE_CD_TIMEOUT = int(environ.get("FSFE_CD_TIMEOUT", 3))
FSFE_CD_PASSPHRASE = environ.get("FSFE_CD_PASSPHRASE", "cmd_passphrase")

# Filename for a temporary lockfile
LOCK_FILENAME = environ.get("LOCK_FILENAME", "/tmp/forms.lock")

# Expiration time for double opt-in confirmation
# (None means no expiration)
CONFIRMATION_EXPIRATION_SECS = 86400

# Parameters for email address validation
VALIDATE_EMAIL_HELO = environ.get("VALIDATE_EMAIL_HELO", "localhost")
VALIDATE_EMAIL_FROM = environ.get("VALIDATE_EMAIL_FROM")


# PostgreSQL database connection string.
SQLALCHEMY_DATABASE_URI = URL.create(
    "postgresql",
    username=environ["POSTGRES_USER"],
    # The password may contain special characters, so we need to encode it.
    password=urllib.parse.quote_plus(environ["POSTGRES_PASSWORD"]),
    host=environ["POSTGRES_HOST"],
    database=environ["POSTGRES_DATABASE"],
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
