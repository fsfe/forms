# =============================================================================
# Functional tests of the "confirm" endpoint
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


def test_confirm(
        client, smtp_mock, redis_mock, file_mock, fsfe_cd_mock, signed_up):
    response = client.get(
            path='/confirm',
            query_string={'id': signed_up})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/success'
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert 'EMAIL@example.com' in logfile
    assert "THE NAME" in logfile
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert email['From'] == 'THE NAME <EMAIL@example.com>'
    # recipients
    assert 'contact@fsfe.org' in email['To']
    # subject
    assert email['Subject'] == "New signature to PMPC"
    # content
    assert "THE NAME" in email.as_string()


def test_confirm_no_id(client):
    response = client.get(
            path='/confirm')
    assert response.status_code == 422


def test_confirm_bad_id(client):
    response = client.get(
            path='/confirm',
            query_string={'id': 'BAD-ID'})
    assert response.status_code == 422
