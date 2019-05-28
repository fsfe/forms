# =============================================================================
# Fixtures for functional tests
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

import pytest
import webtest
from fakeredis import FakeRedis


# -----------------------------------------------------------------------------
# Mocked SMTP connection
# -----------------------------------------------------------------------------

@pytest.fixture
def smtp_mock(mocker):
    return mocker.patch('smtplib.SMTP')


# -----------------------------------------------------------------------------
# Mocked Redis connection
# -----------------------------------------------------------------------------

@pytest.fixture
def redis_mock(mocker):
    return mocker.patch("redis.Redis", FakeRedis)


# -----------------------------------------------------------------------------
# Mocked logfile
# -----------------------------------------------------------------------------

@pytest.fixture
def file_mock(mocker):
    mocker.patch('os.makedirs')
    return mocker.patch(
            'fsfe_forms.common.services.DeliveryService.open',
            mocker.mock_open(read_data="[\n]"))


# -----------------------------------------------------------------------------
# WebTest application interface
# -----------------------------------------------------------------------------

@pytest.fixture
def app(redis_mock):
    # Redis must be patched before we import the app, since the connection is
    # created in module init code.
    from fsfe_forms import wsgi
    return webtest.TestApp(wsgi.application)


# -----------------------------------------------------------------------------
# An already signed up user
# -----------------------------------------------------------------------------

@pytest.fixture
def signed_up(app):
    app.get(
            url='/email',
            params={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    # Return the confirmation ID
    from fsfe_forms.common.services.StorageService import storage
    return storage.keys()[0].split(b':')[-1]
