# =============================================================================
# Queue of registrations pending double opt-in
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
    return json.loads(data.decode('utf-8'))


def _set(id: uuid.UUID, data: dict, ttl: int):
    current_app.queue_db.set(id.hex, json.dumps(data).encode('utf-8'), ttl)


# =============================================================================
# Push a new registration to the queue
# =============================================================================

def queue_push(data: dict) -> uuid.UUID:

    # Check for an unconfirmed previous registration, and if found, update and
    # reuse that one
    for key in current_app.queue_db.keys():
        try:
            id = uuid.UUID(key.decode())
        except ValueError:  # Keys in old format
            continue
        old_data = _get(id)
        if old_data['appid'] == data['appid'] \
                and old_data['confirm'] == data['confirm']:
            _set(id, data, current_app.queue_db.ttl(id.hex))
            return id

    # None found, so generate a new id
    id = uuid.uuid4()
    _set(id, data, current_app.config['CONFIRMATION_EXPIRATION_SECS'])
    return id


# =============================================================================
# Pop a registration from the queue
# =============================================================================

def queue_pop(id: uuid.UUID) -> dict:
    result = _get(id)
    current_app.queue_db.delete(id.hex)
    return result
