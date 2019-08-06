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

def test_email_get(client, smtp_mock, redis_mock, file_mock):
    response = client.get(
            path='/email',
            data={
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
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert email['From'] == 'EMAIL@example.com'
    # recipient
    assert 'contact@fsfe.org' in email['To']
    # subject
    assert email['Subject'] == "EMAIL-SUBJECT"
    # body
    assert "EMAIL-CONTENT" in email.as_string()


def test_email_get_no_params(client):
    response = client.get(
            path='/email')
    assert response.status_code == 422


def test_email_get_bad_appid(client):
    response = client.get(
            path='/email',
            data={'appid': 'BAD-APPID'})
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# With confirmation
# -----------------------------------------------------------------------------

def test_email_get_with_confirmation(client, smtp_mock, redis_mock, file_mock):
    response = client.get(
            path='/email',
            data={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/confirm'
    # Check no logfile written (yet).
    assert not file_mock().write.called
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert 'no-reply@fsfe.org' in email['From']
    # recipient
    assert email['To'] == 'THE NAME <EMAIL@example.com>'
    # subject
    assert email['Subject'] == "Public Code: Please confirm your signature"


def test_email_get_duplicate(
        client, smtp_mock, redis_mock, file_mock, signed_up):
    response = client.get(
            path='/email',
            data={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/confirm'
    # Check no logfile written (yet).
    assert not file_mock().write.called
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert 'no-reply@fsfe.org' in email['From']
    # recipient
    assert email['To'] == 'THE NAME <EMAIL@example.com>'
    # subject
    assert email['Subject'] == "Public Code: Please confirm your signature"


# =============================================================================
# POST method
# =============================================================================

# -----------------------------------------------------------------------------
# Without confirmation
# -----------------------------------------------------------------------------

def test_email_post(client, smtp_mock, redis_mock, file_mock):
    response = client.post(
            path='/email',
            data={
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
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert email['From'] == 'EMAIL@example.com'
    # recipient
    assert 'contact@fsfe.org' in email['To']
    # subject
    assert email['Subject'] == "EMAIL-SUBJECT"
    # content
    assert "EMAIL-CONTENT" in email.as_string()


def test_email_post_no_params(client):
    response = client.post(
            path='/email')
    assert response.status_code == 422


def test_email_post_bad_appid(client):
    response = client.post(
            path='/email',
            data={'appid': 'BAD-APPID'})
    assert response.status_code == 404
