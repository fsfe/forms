# =============================================================================
# Functional tests of the "email" endpoint
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


# =============================================================================
# GET method
# =============================================================================

# -----------------------------------------------------------------------------
# Without confirmation
# -----------------------------------------------------------------------------

def test_email_get(app, smtp_mock, redis_mock, file_mock):
    response = app.get(
            url='/email',
            params={
                'appid': 'contact',
                'from': 'EMAIL@example.com',
                'subject': "EMAIL-SUBJECT",
                'content': "EMAIL-CONTENT"})
    assert response.status_code == 302
    assert response.location == 'https://fsfe.org/contact/'
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert 'EMAIL@example.com' in logfile
    assert "EMAIL-SUBJECT" in logfile
    assert "EMAIL-CONTENT" in logfile
    # Check email sent.
    email = smtp_mock().__enter__().sendmail.call_args[0]
    # sender
    assert email[0] == 'EMAIL@example.com'
    # recipients
    assert email[1] == ['contact@fsfe.org']
    # content
    assert "EMAIL-SUBJECT" in email[2]
    assert "EMAIL-CONTENT" in email[2]


def test_email_get_no_params(app):
    response = app.get(
            url='/email',
            status=400)


def test_email_get_bad_appid(app):
    response = app.get(
            url='/email',
            params={'appid': 'BAD-APPID'},
            status=404)


# -----------------------------------------------------------------------------
# With confirmation
# -----------------------------------------------------------------------------

def test_email_get_with_confirmation(app, smtp_mock, redis_mock, file_mock):
    response = app.get(
            url='/email',
            params={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/confirm'
    # Check no logfile written (yet).
    # FIXME: Writes an "empty" logfile, but this would not be necessary here.
    assert file_mock().write.call_args[0][0] == "[]"
    # Check email sent.
    email = smtp_mock().__enter__().sendmail.call_args[0]
    # sender
    assert email[0] == 'no-reply@fsfe.org'
    # recipients
    assert email[1] == ['EMAIL@example.com']
    # content
    assert "Subject: Public Code: Please confirm your signature" in email[2]


def test_email_get_duplicate(app, smtp_mock, redis_mock, file_mock, signed_up):
    response = app.get(
            url='/email',
            params={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/confirm'
    # Check no logfile written (yet).
    # FIXME: Writes an "empty" logfile, but this would not be necessary here.
    assert file_mock().write.call_args[0][0] == "[]"
    # Check email sent.
    email = smtp_mock().__enter__().sendmail.call_args[0]
    # sender
    assert email[0] == 'no-reply@fsfe.org'
    # recipients
    assert email[1] == ['EMAIL@example.com']
    # content
    assert "Subject: Public Code: Please confirm your signature" in email[2]


# =============================================================================
# POST method
# =============================================================================

# -----------------------------------------------------------------------------
# Without confirmation
# -----------------------------------------------------------------------------

def test_email_post(app, smtp_mock, redis_mock, file_mock):
    response = app.post(
            url='/email',
            params={
                'appid': 'contact',
                'from': 'EMAIL@example.com',
                'subject': "EMAIL-SUBJECT",
                'content': "EMAIL-CONTENT"})
    assert response.status_code == 302
    assert response.location == 'https://fsfe.org/contact/'
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert 'EMAIL@example.com' in logfile
    assert "EMAIL-SUBJECT" in logfile
    assert "EMAIL-CONTENT" in logfile
    # Check email sent.
    email = smtp_mock().__enter__().sendmail.call_args[0]
    # sender
    assert email[0] == 'EMAIL@example.com'
    # recipients
    assert email[1] == ['contact@fsfe.org']
    # content
    assert "EMAIL-SUBJECT" in email[2]
    assert "EMAIL-CONTENT" in email[2]


def test_email_post_no_params(app):
    response = app.post(
            url='/email',
            status=400)


def test_email_post_bad_appid(app):
    response = app.post(
            url='/email',
            params={'appid': 'BAD-APPID'},
            status=404)
