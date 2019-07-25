# =============================================================================
# WSGI application
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

import json
import os
from logging import ERROR, INFO, Formatter, getLogger
from logging.handlers import SMTPHandler

from flask import Flask
from flask.logging import default_handler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from fsfe_forms.common import config
from fsfe_forms.email import init_email
from fsfe_forms.views import email, confirm


# =============================================================================
# Main application factory
# =============================================================================

def create_app(testing=False):
    app = Flask(__name__.split('.')[0])

    # This enables Flask-Limiter to detect the real remote address even though
    # fsfe-forms runs behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # Read configuration
    app.config.from_object(config)
    if testing:
        app.config['TESTING'] = True

    # Configure the root logger
    root_logger = getLogger()
    root_logger.setLevel(INFO)

    # Add the flask default log handler
    default_handler.setFormatter(Formatter(
        '[%(asctime)s] (%(name)s) %(levelname)s: %(message)s'))
    root_logger.addHandler(default_handler)

    # Add a log handler which forwards errors by email
    if not (app.debug or app.testing):  # pragma: no cover
        if app.config['MAIL_USERNAME'] is not None:
            credentials = (
                    app.config['MAIL_USERNAME'],
                    app.config['MAIL_PASSWORD'])
        else:
            credentials = None
        handler = SMTPHandler(
                mailhost=(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT']),
                fromaddr=app.config['LOG_EMAIL_FROM'],
                toaddrs=[app.config['LOG_EMAIL_TO']],
                subject="Log message from fsfe-forms",
                credentials=credentials)
        handler.setLevel(ERROR)
        root_logger.addHandler(handler)

    # Initialize Flask-Limiter
    app.limiter = Limiter(app, key_func=get_remote_address)

    # Initialize our own email module
    init_email(app)

    # Load application configurations
    filename = os.path.join(os.path.dirname(__file__), 'applications.json')
    with open(filename) as f:
        app.app_configs = json.load(f)

    # Register views
    app.add_url_rule(rule="/email", view_func=email, methods=["GET", "POST"])
    app.add_url_rule(rule="/confirm", view_func=confirm)

    return app
