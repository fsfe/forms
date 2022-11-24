# =============================================================================
# Email delivery based on a Jinja2 template
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import email
import email.charset
import email.policy
import email.utils
import smtplib
from typing import Optional

from flask import current_app, render_template


# =============================================================================
# Initialize this module
# =============================================================================


def init_email(app):

    # Change default transfer-encoding for utf-8 to 'quoted-printable'
    email.charset.add_charset("utf-8", email.charset.QP, email.charset.QP)

    # Set up a policy for rendering templates into an email message
    email.policy.render = email.policy.default.clone(refold_source="all")

    # Make 'format_email' function available to templates
    @app.context_processor
    def context_processor():
        def format_email(name, address):
            return email.utils.formataddr((name, address))

        return {"format_email": format_email}


# =============================================================================
# Send out an email
# =============================================================================


def send_email(template: str, lang: Optional[str] = None, **kwargs):

    # Compile list of template filenames to look for
    template_list = []
    if lang is not None:
        template_list.append(f"{template}.{lang}.eml")
    template_list.append(f"{template}.eml")

    # Prepare message from template
    message = email.message_from_string(
        render_template(template_list, **kwargs), policy=email.policy.render
    )

    # Add some standard headers
    if "From" in message:
        message["Sender"] = "FSFE form server <contact@fsfe.org>"
    else:
        message["From"] = "Free Software Foundation Europe <contact@fsfe.org>"
    message["Date"] = email.utils.localtime()
    message["Message-ID"] = email.utils.make_msgid(
        domain=current_app.config["MAIL_HELO_HOST"]
    )
    # message['Auto-Submitted'] = 'auto-generated'  # OTRS doesn't like this

    # Tell the library which character set to use on serialization
    message.set_charset("utf-8")

    # Send out the message
    with smtplib.SMTP(
        host=current_app.config["MAIL_SERVER"],
        port=current_app.config["MAIL_PORT"],
        local_hostname=current_app.config["MAIL_HELO_HOST"],
    ) as smtp:
        if current_app.config["MAIL_USERNAME"]:
            smtp.login(
                user=current_app.config["MAIL_USERNAME"],
                password=current_app.config["MAIL_PASSWORD"],
            )
        try:
            smtp.send_message(message)
        except smtplib.SMTPRecipientsRefused:
            # Ignore errors from invalid email addresses entered
            pass

    return message
