# =============================================================================
# Functional tests of the "index" endpoint
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
