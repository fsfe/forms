# =============================================================================
# WSGI application
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2017-2019 Free Software Foundation Europe <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import logging.handlers
import os

import redis
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from fsfe_forms import config
from fsfe_forms.email import init_email
from fsfe_forms.views import confirm, email, index


# =============================================================================
# Main application factory
# =============================================================================

def create_app():
    app = Flask(__name__.split('.')[0])

    # This enables Flask-Limiter to detect the real remote address even though
    # fsfe-forms runs behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Read configuration
    app.config.from_object(config)

    # Configure the root logger
    logging.basicConfig(
            format='[%(asctime)s] (%(name)s) %(levelname)s: %(message)s',
            level=(logging.DEBUG if app.debug else logging.INFO))

    # Add a log handler which forwards errors by email
    if not (app.debug or app.testing):  # pragma: no cover
        if app.config['MAIL_USERNAME'] is not None:
            credentials = (
                    app.config['MAIL_USERNAME'],
                    app.config['MAIL_PASSWORD'])
        else:
            credentials = None
        handler = logging.handlers.SMTPHandler(
                mailhost=(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT']),
                fromaddr=app.config['LOG_EMAIL_FROM'],
                toaddrs=[app.config['LOG_EMAIL_TO']],
                subject="Log message from fsfe-forms",
                credentials=credentials)
        handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(handler)

    # Initialize Flask-Limiter
    app.limiter = Limiter(app, key_func=get_remote_address)

    # Initialize our own email module
    init_email(app)

    # Initialize Redis store for double opt-in queue
    app.queue_db = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            password=app.config['REDIS_PASSWORD'],
            db=app.config['REDIS_QUEUE_DB'])

    # Load application configurations
    filename = os.path.join(os.path.dirname(__file__), 'applications.json')
    with open(filename) as f:
        app.app_configs = json.load(f)

    # Register views
    app.add_url_rule(rule="/", view_func=index)
    app.add_url_rule(rule="/email", view_func=email, methods=["GET", "POST"])
    app.add_url_rule(rule="/confirm", view_func=confirm)

    return app
