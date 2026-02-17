"""Fixtures for functional tests.

This file is part of the FSFE Form Server.
"""

import pytest
from fakeredis import FakeRedis
from flask import url_for
from requests import Response

from fsfe_forms import config, create_app


EML: str = "EMAIL@example.com"
NAME: str = "THE NAME"


@pytest.fixture
def smtp_mock(mocker):
    return mocker.patch("smtplib.SMTP")


@pytest.fixture
def redis_mock(mocker):
    return mocker.patch("redis.Redis", FakeRedis)


@pytest.fixture
def file_mock(mocker):
    """Mock the logfile."""
    mocker.patch("os.makedirs")
    return mocker.patch(
        "fsfe_forms.json_store.open", mocker.mock_open(read_data="[\n]")
    )


@pytest.fixture
def fsfe_cd_mock(mocker):
    response = Response()
    response.status_code = 200
    response._content = b'{"id": "FSFE_CD_ID"}'
    return mocker.patch(target="fsfe_forms.cd.post", return_value=response)


@pytest.fixture
def app(redis_mock):
    """Mock the WebTest application interface."""
    config.TESTING = True
    return create_app()


@pytest.fixture
def signed_up(client, smtp_mock):
    """Mock a signed up user."""
    client.get(
        path="/email",
        query_string={
            "appid": "ln-apply",
            "name": NAME,
            "confirm": EML,
            "activities": "MY ACTIVITIES",
            "obligatory": "yes",
        },
    )
    # Return the confirmation ID
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    for line in email.as_string().splitlines():
        if url_for("confirm") in line:
            return line.split("=3D")[-1]
    return None
