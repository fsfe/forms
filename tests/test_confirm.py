"""Functional tests of the "confirm" and "redeem" endpoint.

This file is part of the FSFE Form Server.
"""

from http import HTTPStatus

from .conftest import EML


def test_confirm_redeem_id(client, signed_up):
    """Confirm landing page with a valid ID"""
    response = client.get(path="/confirm", query_string={"id": signed_up})
    assert response.status_code == HTTPStatus.OK
    assert bytes(f'<a href="/redeem?id={signed_up}"', "utf-8") in response.data


def test_confirm_no_id(client):
    """Confirm landing page without an ID"""
    response = client.get(path="/confirm")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_confirm_bad_id(client):
    """Confirm landing page with a malformed ID"""
    response = client.get(path="/confirm", query_string={"id": "BAD-ID"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_redeem(client, smtp_mock, redis_mock, file_mock, fsfe_cd_mock, signed_up):
    """Redeem a valid ID"""
    name: str = "THE NAME"

    response = client.get(path="/redeem", query_string={"id": signed_up})
    assert response.status_code == HTTPStatus.FOUND
    assert (
        response.location == "https://fsfe.org/activities/ln/"
        "application-success.html"
    )
    # Check logfile written.
    logfile = file_mock().write.call_args[0][0]
    assert EML in logfile
    assert name in logfile
    # Check email sent.
    email = smtp_mock().__enter__().send_message.call_args[0][0]
    # sender
    assert email["From"] == f"{name} <{EML}>"
    # recipients
    assert email["To"] in [
        "Free Software Foundation Europe <contact@fsfe.org>",
        "Free Software Foundation Europe <helpdesk@fsfe.org>",
    ]
    # subject
    assert email["Subject"] == f"Application for Legal Network membership by {name}"
    # content
    assert "MY ACTIVITIES" in email.as_string()


def test_redeem_doubled(client, signed_up):
    """Redeem the same valid ID more than once"""
    client.get(path="/redeem", query_string={"id": signed_up})
    response = client.get(path="/redeem", query_string={"id": signed_up})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert b"No such pending confirmation ID" in response.data


def test_redeem_no_id(client):
    """Redeem without an ID"""
    response = client.get(path="/redeem")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_redeem_bad_id(client):
    """Redeem with a malformed ID"""
    response = client.get(path="/redeem", query_string={"id": "BAD-ID"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
