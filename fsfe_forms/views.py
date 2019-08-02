# =============================================================================
# Endpoints for the WSGI server
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

from flask import (
        abort, current_app, redirect, render_template, request, url_for)
from marshmallow.validate import Regexp
from webargs.fields import String, UUID
from webargs.flaskparser import parser, use_kwargs

from fsfe_forms.common.services import DeliveryService
from fsfe_forms.email import send_email
from fsfe_forms.queue import queue_pop, queue_push


# =============================================================================
# Helper functions
# =============================================================================

# -----------------------------------------------------------------------------
# Find application config or issue 404 error
# -----------------------------------------------------------------------------

def _find_app_config(appid):
    try:
        return current_app.app_configs[appid]
    except KeyError:
        abort(404, f'No application configuration for "{appid}"')


# -----------------------------------------------------------------------------
# Send email, store data, and redirect
# -----------------------------------------------------------------------------

def _process(config, params, id=None, store=None):

    # Send out email
    message = send_email(
            template=config['email'],
            confirmation_url=url_for('confirm', _external=True, id=id),
            **params)

    # Store data in JSON log
    if store:
        DeliveryService.log(
                store,
                message['From'],
                [message['To']],
                message['Subject'],
                message.get_content(),
                message['Reply-To'],
                params)

    # Redirect the user's browser
    return redirect(config['redirect'])


# =============================================================================
# Index endpoint (shows static information page)
# =============================================================================

def index():
    return render_template("index.html")


# =============================================================================
# Registration endpoint
# =============================================================================

email_parameters = {
        "appid": String(required=True),
        "lang": String(validate=Regexp('^[a-z]{2}$'), missing=None)}


@use_kwargs(email_parameters)
def email(appid, lang):
    # Load application configuration
    app_config = _find_app_config(appid)

    # Load dictionary of all request parameters
    params = dict(request.values)

    # Validate required parameters
    for field in app_config['required_vars']:
        if field not in params:
            raise abort(400, f'"{field}" is required')

    if 'confirm' in app_config:         # With double opt-in
        if params.get('confirm') is None:
            abort(400, '"Confirm" address is required')

        # Optionally, check for a confirmed previous registration, and if
        # found, refuse the duplicate
        if 'duplicate' in app_config \
                and DeliveryService.find(
                        app_config['store'],
                        params['confirm']):
            return _process(
                    config=app_config['duplicate'],
                    params=params)
        else:
            id = queue_push(params)
            return _process(
                    config=app_config['register'],
                    params=params,
                    id=id)
    else:                               # Without double opt-in
        return _process(
                config=app_config['register'],
                params=params,
                store=app_config.get('store'))


# =============================================================================
# Confirmation endpoint
# =============================================================================

confirm_parameters = {
        "id": UUID(required=True)}


@use_kwargs(confirm_parameters)
def confirm(id):
    params = queue_pop(id)

    app_config = _find_app_config(params['appid'])

    return _process(
            config=app_config['confirm'],
            params=params,
            store=app_config['store'])
