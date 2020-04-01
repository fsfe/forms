# =============================================================================
# Fixtures for functional tests
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from fakeredis import FakeRedis
from flask import url_for

from fsfe_forms import config, create_app


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
            'fsfe_forms.json_store.open',
            mocker.mock_open(read_data="[\n]"))


# -----------------------------------------------------------------------------
# WebTest application interface
# -----------------------------------------------------------------------------

@pytest.fixture
def app(redis_mock):
    config.TESTING = True
    return create_app()


# -----------------------------------------------------------------------------
# An already signed up user
# -----------------------------------------------------------------------------

@pytest.fixture
def signed_up(client, smtp_mock):
    client.get(
            path='/email',
            query_string={
                'appid': 'pmpc-sign',
                'name': "THE NAME",
                'confirm': 'EMAIL@example.com'})
    # Return the confirmation ID
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    for line in email.as_string().splitlines():
        if url_for('confirm') in line:
            return line.split('=3D')[-1]
