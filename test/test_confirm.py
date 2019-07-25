# =============================================================================
# Functional tests of the "confirm" endpoint
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


def test_confirm(client, smtp_mock, redis_mock, file_mock, signed_up):
    response = client.get(
            path='/confirm',
            data={'id': signed_up})
    assert response.status_code == 302
    assert response.location == 'https://publiccode.eu/openletter/success'
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert 'EMAIL@example.com' in logfile
    assert "THE NAME" in logfile
    # Check email sent.
    email = smtp_mock().__enter__().sendmail.call_args[0]
    # sender
    assert email[0] == 'admin@fsfe.org'
    # recipients
    assert email[1] == ['contact@fsfe.org']
    # content
    assert "Subject: New signature to PMPC" in email[2]
    assert "THE NAME" in email[2]


def test_confirm_no_id(client):
    response = client.get(
            path='/confirm')
    assert response.status_code == 422


# FIXME: not well handled yet.
#def test_confirm_bad_id(client):
#    response = client.get(
#            path='/confirm',
#            data={'id': 'BAD-ID'},
#    assert response.status_code == 404
