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


def _get(the_id: uuid.UUID) -> dict:
    """Helper function to read a dictionary from Redis"""
    data = current_app.queue_db.get(the_id.hex)
    if data is None:
        abort(404, "No such pending confirmation ID")
    return json.loads(data.decode("utf-8"))


def _set(the_id: uuid.UUID, data: dict, ttl: int):
    """Helper function to write a dictionary to Redis"""
    current_app.queue_db.set(the_id.hex, json.dumps(data).encode("utf-8"), ttl)


def queue_push(data: dict) -> uuid.UUID:
    """Push a new registration to the queue"""

    # Check for an unconfirmed previous registration, and if found, update and
    # reuse that one
    for existing_id in [
        uuid.UUID(key.decode()) for key in current_app.queue_db.keys()  # noqa: SIM118
    ]:
        old_data = _get(existing_id)
        if (
            old_data["appid"] == data["appid"]
            and old_data["confirm"] == data["confirm"]
        ):
            _set(existing_id, data, current_app.queue_db.ttl(existing_id.hex))
            current_app.logger.info("UUID reused:", existing_id)
            return existing_id

    # None found, so generate a new id
    the_id = uuid.uuid4()
    _set(the_id, data, current_app.config["CONFIRMATION_EXPIRATION_SECS"])
    current_app.logger.info("UUID created:", the_id)
    return the_id


def queue_pop(the_id: uuid.UUID) -> dict:
    """Pop a registration from the queue"""
    rval: dict = _get(the_id)
    current_app.queue_db.delete(the_id.hex)
    current_app.logger.info("UUID deleted:", the_id)
    return rval
