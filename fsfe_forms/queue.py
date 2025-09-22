"""Queue of registrations pending double opt-in"""

# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import uuid

from flask import abort, current_app


# =============================================================================
# Helper functions to read and write a dictionary to and from Redis
# =============================================================================


def _get(id: uuid.UUID) -> dict:
    data = current_app.queue_db.get(id.hex)
    if data is None:
        abort(404, "No such pending confirmation ID")
    return json.loads(data.decode("utf-8"))


def _set(id: uuid.UUID, data: dict, ttl: int):
    current_app.queue_db.set(id.hex, json.dumps(data).encode("utf-8"), ttl)


# =============================================================================
# Push a new registration to the queue
# =============================================================================


def queue_push(data: dict) -> uuid.UUID:

    # Check for an unconfirmed previous registration, and if found, update and
    # reuse that one
    for id in [uuid.UUID(key.decode()) for key in current_app.queue_db.keys()]:
        old_data = _get(id)
        if (
            old_data["appid"] == data["appid"]
            and old_data["confirm"] == data["confirm"]
        ):
            _set(id, data, current_app.queue_db.ttl(id.hex))
            current_app.logger.info(f"UUID {id} reused")
            return id

    # None found, so generate a new id
    id = uuid.uuid4()
    _set(id, data, current_app.config["CONFIRMATION_EXPIRATION_SECS"])
    current_app.logger.info(f"UUID {id} created")
    return id


# =============================================================================
# Pop a registration from the queue
# =============================================================================


def queue_pop(id: uuid.UUID) -> dict:
    result = _get(id)
    current_app.queue_db.delete(id.hex)
    current_app.logger.info(f"UUID {id} deleted")
    return result
