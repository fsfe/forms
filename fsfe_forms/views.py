# =============================================================================
# Endpoints for the WSGI server
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import (
    abort, current_app, redirect, render_template, render_template_string,
    request, url_for)
from marshmallow import Schema
from marshmallow.fields import UUID, Boolean, Email, String
from marshmallow.validate import Equal, Length, Regexp
from validate_email import validate_email
from webargs.flaskparser import use_kwargs

from fsfe_forms import json_store
from fsfe_forms.cd import subscribe
from fsfe_forms.email import send_email
from fsfe_forms.queue import queue_pop, queue_push


# =============================================================================
# Exception classes
# =============================================================================


class AppConfigError(Exception):
    def __init__(self, message):
        self.message = f"Error in application configuration: {message}"


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
# Validate parameters
# -----------------------------------------------------------------------------


def _validate(config: dict, params: dict, confirm: bool):  # noqa

    current_app.logger.debug(f"config: {config}")
    current_app.logger.debug(f"params: {params}")
    current_app.logger.debug(f"confirm: {confirm}")
    # Build Marshmallow Schema from configuration
    fields = {
        "appid": String(required=True),
        "lang": String(validate=Regexp(r"^[a-z]{2}$"), missing=None),
    }
    if confirm:
        fields["confirm"] = Email(required=True)

        # Don't do expensive email validation during testing
        if current_app.testing or current_app.debug:
            result = True

        else:
            # Abort immediately on blacklisted domains
            blacklisted_email_domains = [
                "aol.com",
                "inbox.ru",
                "list.ru",
                "mail.ru",
                "yahoo.com",
            ]
            try:
                if params["confirm"].split("@")[1] in blacklisted_email_domains:
                    abort(422, "Your email provider is temporarily blocked.")
            except KeyError:
                abort(422, "Your email address didn't pass initial validation.")
            except IndexError:
                abort(422, "Your email address didn't pass initial validation.")

            # Do expensive validation
            result = validate_email(
                email_address=params["confirm"],
                smtp_helo_host=current_app.config["VALIDATE_EMAIL_HELO"],
                smtp_from_address=current_app.config["VALIDATE_EMAIL_FROM"],
            )
            if result is False:
                current_app.logger.info(
                    "Caught invalid email address '{}'".format(params["confirm"])
                )
                abort(422, "This email address does not exist.")
            elif result is None:
                current_app.logger.warning(
                    "Could not verify email address '{}'".format(params["confirm"])
                )

    for name, options in config.items():
        field_class = String
        validate = []
        required = False
        for opt in options:
            if opt == "boolean":
                field_class = Boolean
            elif opt == "email":
                field_class = Email
            elif opt == "forbidden":
                validate.append(Length(equal=0))
            elif opt == "mandatory":
                field_class = Boolean
                required = True
                validate.append(Equal(True, error="Mandatory."))
            elif opt == "required":
                required = True
            elif opt == "single-line":
                validate.append(Regexp(r"^[^\r\n]*$"))
            else:
                raise AppConfigError("Invalid option {opt} for parameter {name}")
        kwargs = {"required": required, "validate": validate}
        if not required:
            kwargs["missing"] = None
        fields[name] = field_class(**kwargs)
    schema = Schema.from_dict(fields)()

    # Do the actual validation; don't use the deserialized values because we
    # want for example "yes" to remain "yes" and not change to True
    errors = schema.validate(params)
    if errors:
        messages = [k + ": " + " ".join(v) for k, v in errors.items()]
        abort(422, "\n".join(messages))


# -----------------------------------------------------------------------------
# Send email, store data, and redirect
# -----------------------------------------------------------------------------


def _process(config, params, id=None, store=None):

    if "email" in config:
        # Send out email
        message = send_email(
            template=config["email"],
            confirmation_url=url_for("confirm", _external=True, id=id),
            **params,
        )

        # Store data in JSON log
        if store:
            json_store.log(
                store,
                message["From"],
                [message["To"]],
                message["Subject"],
                message.get_content(),
                message["Reply-To"],
                params,
            )
    else:
        # Store data in JSON log without having sent an email
        if store:
            json_store.log(store, "", [""], "", "", "", params)

    # Redirect the user's browser
    return redirect(render_template_string(config["redirect"], **params))


# =============================================================================
# Index endpoint (shows static information page)
# =============================================================================


def index():
    return render_template("pages/index.html")


# =============================================================================
# Registration endpoint
# =============================================================================


def email():
    # Remove all empty parameters
    params = {k: v for k, v in request.values.items() if v != ""}

    # Load application configuration
    app_config = _find_app_config(params.get("appid"))

    # Validate required parameters
    _validate(app_config["parameters"], params, "confirm" in app_config)

    if "confirm" in app_config:  # With double opt-in
        # Optionally, check for a confirmed previous registration, and if
        # found, refuse the duplicate
        if "duplicate" in app_config and json_store.find(
            app_config["store"], params["confirm"]
        ):
            return _process(config=app_config["duplicate"], params=params)
        else:
            id = queue_push(params)
            return _process(config=app_config["register"], params=params, id=id)
    else:  # Without double opt-in
        return _process(
            config=app_config["register"], params=params, store=app_config.get("store")
        )


# =============================================================================
# Confirmation endpoint
# =============================================================================

confirm_parameters = {"id": UUID(required=True)}


@use_kwargs(confirm_parameters, location="query")
def confirm(id):
    """A landing page to confirm the ID via a click. Hands over to redeem()"""
    return render_template("pages/confirm.html", id=id)


@use_kwargs(confirm_parameters, location="query")
def redeem(id):
    """Redeems an ID after checking its validity, refers to further actions then"""
    params = queue_pop(id)

    app_config = _find_app_config(params["appid"])

    if "cd" in app_config:
        response = subscribe(app_config["cd"], params)
        # If the FSFE Community Database has yielded an error message, display
        # it unchanged.
        if response:
            return response

    return _process(
        config=app_config["confirm"], params=params, store=app_config["store"]
    )
