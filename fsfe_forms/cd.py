# =============================================================================
# Interaction with the FSFE Community Database
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import date
from hashlib import sha256

from flask import current_app
from requests import post


# =============================================================================
# Subscribe an email address in the FSFE Community Database
# =============================================================================


def subscribe(config, params):

    subscribe_params = {
        "referrer": "campaign:" + params["appid"],
        "email1": params["confirm"],
    }
    if "lang" in params:
        subscribe_params["language"] = params["lang"]
    confirm_params = {}

    # We delay the signed_*_on and wants_*_info parameters to the confirmation
    # step. Otherwise, they would not be updated on existing registrations in
    # the Community Database.
    for key, value in config.items():
        if value == "<date>":
            value = str(date.today())
        else:
            value = params.get(value)
        if not value:
            continue
        if (
            key.startswith("signed_")
            and key.endswith("_on")
            or key.startswith("wants_")
            and key.endswith("_info")
        ):
            confirm_params[key] = value
        else:
            subscribe_params[key] = value

    # First step: POST registration data to FSFE Community Database.

    response = post(
        url=current_app.config["FSFE_CD_URL"] + "subscribe-api",
        timeout=current_app.config["FSFE_CD_TIMEOUT"],
        data=subscribe_params,
    )
    if not response.ok:
        # In case of an error, fsfe-cd returns a HTML page with a
        # human-readable error description, which we just forward unchanged to
        # the user.
        return response.text, response.status_code
    person_id = response.json()["id"]

    # Second step: Automatically confirm the registration.

    # Determine command signature
    parts = ["command=persons.confirm", f"record_id={person_id}"]
    for key in sorted(confirm_params.keys()):
        parts.append("{}={}".format(key, confirm_params[key]))
    parts.append(current_app.config["FSFE_CD_PASSPHRASE"])
    signature = sha256(";".join(parts).encode("UTF-8")).hexdigest()

    # Note that the data parameters are in the query string, while the "go"
    # parameter is in the form data.
    confirm_params["person"] = person_id
    confirm_params["signature"] = signature
    response = post(
        url=current_app.config["FSFE_CD_URL"] + "command/confirm",
        timeout=current_app.config["FSFE_CD_TIMEOUT"],
        params=confirm_params,
        data={"go": "1"},
    )
    if not response.ok:
        # In case of an error, fsfe-cd returns a HTML page with a
        # human-readable error description, which we just forward unchanged to
        # the user.
        return response.text, response.status_code
