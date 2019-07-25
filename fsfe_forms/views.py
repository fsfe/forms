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

from flask import redirect, request
from webargs.fields import String
from webargs.flaskparser import use_kwargs

from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import SenderService


# =============================================================================
# Registration endpoint
# =============================================================================

email_parameters = {
        "appid": String(required=True)}


@use_kwargs(email_parameters)
def email(appid):
    send_data = SendData.from_request(appid, request.values, request.url)
    config = SenderService.validate_and_send_email(send_data)
    return redirect(config.redirect)


# =============================================================================
# Confirmation endpoint
# =============================================================================

confirm_parameters = {
        "id": String(required=True)}


@use_kwargs(confirm_parameters)
def confirm(id):
    config = SenderService.confirm_email(id)
    return redirect(config.redirect_confirmed or config.redirect)
