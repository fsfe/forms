"""Endpoints for the WSGI server"""

# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import (
    abort,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)
from marshmallow import Schema
from marshmallow.fields import UUID, Boolean, Email, String
from marshmallow.validate import Equal, Length, Regexp
from validate_email import validate_email
from webargs.flaskparser import use_kwargs

from fsfe_forms import json_store
from fsfe_forms.cd import subscribe
from fsfe_forms.email import send_email
from fsfe_forms.queue import queue_pop, queue_push


class AppConfigError(Exception):
    def __init__(self, message):
        self.message = f"Error in application configuration: {message}"


# =============================================================================
# Helper functions
# =============================================================================


def _find_app_config(appid):
    """# Find application config or issue 404 error"""
    try:
        return current_app.app_configs[appid]
    except KeyError:
        abort(404, f'No application configuration for "{appid}"')


# -----------------------------------------------------------------------------
# Custom additions to domain blocklist
# -----------------------------------------------------------------------------

domain_blacklist: set[str] = {
    # Emails from these domains were used en masse to sign-up to our
    # services or sign open letters which sometimes landed our SMTP server
    # on several blocklists. Blocking these domains entirely fixes the
    # issue.
    "inbox.ru",
    "list.ru",
    "mail.ru",
    "aol.com",
    "yahoo.com",
    "ymail.com",
}


def _validate(config: dict, params: dict, confirm: bool) -> None:
    """Validate parameters"""
    current_app.logger.debug("config: %s", config)
    current_app.logger.debug("params: %s", params)
    current_app.logger.debug("confirm: %s", confirm)
    # Build Marshmallow Schema from configuration
    fields = {
        "appid": String(required=True),
        "lang": String(validate=Regexp(r"^[a-z]{2}$"), load_default=None),
    }
    if confirm:
        # Do syntax check
        fields["confirm"] = Email(required=True)

        # Don't do expensive email validation in testing
        if current_app.testing or current_app.debug:
            return

        try:
            # Check if email is in custom blacklist
            if params["confirm"].split("@")[-1] in domain_blacklist:
                current_app.logger.info(
                    "Email address is on domain blacklist: %s", params["confirm"]
                )
                abort(
                    422,
                    "Using this email address is not possible. Please try another one.",
                )

            # Do expensive validation
            result = validate_email(
                email_address=params["confirm"],
                smtp_helo_host=current_app.config["VALIDATE_EMAIL_HELO"],
                smtp_from_address=current_app.config["VALIDATE_EMAIL_FROM"],
            )
            if result is False:
                current_app.logger.info(
                    "Caught invalid email address: %s", params["confirm"]
                )
                abort(
                    422,
                    "Using this email address is not possible. Please try another one.",
                )
            elif result is None:
                current_app.logger.warning(
                    "Could not verify email address: %s", params["confirm"]
                )
        except KeyError:
            current_app.logger.warning("Could not validate email address.")
            current_app.logger.info("config: %s", config)
            current_app.logger.info("params: %s", params)
            current_app.logger.info("confirm: %s", confirm)

    for name, options in config.items():
        field_class = String
        validate = []
        required = False
        for opt in options:
            match opt:
                case "boolean":
                    field_class = Boolean
                case "email":
                    field_class = Email
                case "forbidden":
                    validate.append(Length(equal=0))
                case "mandatory":
                    field_class = Boolean
                    required = True
                    validate.append(Equal(True, error="Mandatory."))
                case "required":
                    required = True
                case "single-line":
                    validate.append(Regexp(r"^[^\r\n]*$"))
                case _:
                    raise AppConfigError(f"Invalid option {opt} for parameter {name}")
        kwargs = {"required": required, "validate": validate}
        if not required:
            kwargs["load_default"] = None
        fields[name] = field_class(**kwargs)
    schema = Schema.from_dict(fields)()

    # Do the actual validation; don't use the deserialized values because we
    # want for example "yes" to remain "yes" and not change to True
    errors = schema.validate(params)
    if errors:
        messages = [k + ": " + " ".join(v) for k, v in errors.items()]
        abort(422, "\n".join(messages))


def _process(config, params, id=None, store=None) -> str:
    """Send email, store data, and redirect"""

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
    elif store:  # Store data in JSON log without having sent an email
        json_store.log(store, "", [""], "", "", "", params)

    # Redirect the user's browser
    return redirect(render_template_string(config["redirect"], **params))


def index():
    """Index endpoint (shows static information page)"""
    return render_template("pages/index.html")


def email():
    """Registration endpoint"""
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
        # else
        return _process(
            config=app_config["register"], params=params, id=queue_push(params)
        )
    # Without double opt-in
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
