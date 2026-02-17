"""Functional tests of the "email" endpoint.

This file is part of the FSFE Form Server.
"""

from http import HTTPStatus

from .conftest import EML, FSFE_ADDRS, NAME


# =============================================================================
# GET method
# =============================================================================

# -----------------------------------------------------------------------------
# Without confirmation
# -----------------------------------------------------------------------------


def test_email_get(client, smtp_mock, redis_mock, file_mock):
    response = client.get(
        path="/email",
        query_string={
            "appid": "contact",
            "from": EML,
            "subject": "EMAIL-SUBJECT",
            "content": "EMAIL-CONTENT",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "https://fsfe.org/contact/"
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert EML in logfile
    assert "EMAIL-SUBJECT" in logfile
    assert "EMAIL-CONTENT" in logfile
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    assert email["From"] == EML
    assert email["To"] in FSFE_ADDRS
    assert email["Subject"] == "EMAIL-SUBJECT"
    assert "EMAIL-CONTENT" in email.as_string()


def test_email_get_no_params(client):
    response = client.get(path="/email")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_email_get_bad_appid(client):
    response = client.get(path="/email", query_string={"appid": "BAD-APPID"})
    assert response.status_code == HTTPStatus.NOT_FOUND


# -----------------------------------------------------------------------------
# With confirmation
# -----------------------------------------------------------------------------


def test_email_get_with_confirmation(client, smtp_mock, redis_mock, file_mock):
    response = client.get(
        path="/email",
        query_string={
            "appid": "pmpc-sign",
            "name": NAME,
            "confirm": EML,
            "lang": "en",
            "permissionPriv": "yes",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "https://publiccode.eu/en/openletter/confirm"
    # Check no logfile written (yet).
    assert not file_mock().write.called
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    assert "no-reply@fsfe.org" in email["From"]
    assert email["To"] == f"{NAME} <{EML}>"
    assert email["Subject"] == "Public Code: Please confirm your signature"


def test_email_get_duplicate(client, smtp_mock, redis_mock, file_mock, signed_up):
    response = client.get(
        path="/email",
        query_string={
            "appid": "pmpc-sign",
            "name": NAME,
            "confirm": EML,
            "lang": "en",
            "permissionPriv": "yes",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "https://publiccode.eu/en/openletter/confirm"
    # Check no logfile written (yet).
    assert not file_mock().write.called
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    assert "no-reply@fsfe.org" in email["From"]
    assert email["To"] == f"{NAME} <{EML}>"
    assert email["Subject"] == "Public Code: Please confirm your signature"


# =============================================================================
# POST method
# =============================================================================

# -----------------------------------------------------------------------------
# Without confirmation
# -----------------------------------------------------------------------------


def test_email_post(client, smtp_mock, redis_mock, file_mock):
    response = client.post(
        path="/email",
        data={
            "appid": "contact",
            "from": EML,
            "subject": "EMAIL-SUBJECT",
            "content": "EMAIL-CONTENT",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "https://fsfe.org/contact/"

    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert EML in logfile
    assert "EMAIL-SUBJECT" in logfile
    assert "EMAIL-CONTENT" in logfile

    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    assert email["From"] == EML
    assert email["To"] in FSFE_ADDRS
    assert email["Subject"] == "EMAIL-SUBJECT"
    assert "EMAIL-CONTENT" in email.as_string()


def test_email_post_no_params(client):
    response = client.post(path="/email")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_email_post_bad_appid(client):
    response = client.post(path="/email", data={"appid": "BAD-APPID"})
    assert response.status_code == HTTPStatus.NOT_FOUND
