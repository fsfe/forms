# =============================================================================
# Functional tests of the "index" endpoint
# =============================================================================
# This file is part of the FSFE Form Server.


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
