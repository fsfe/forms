# =============================================================================
# Storage of (confirmed) request data in a JSON file
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
import os
import time

import filelock
from flask import current_app


def log(storage, send_from, send_to, subject, content, reply_to, include_vars):
    add = {
        "timestamp": time.time(),
        "from": send_from,
        "to": send_to,
        "subject": subject,
        "content": content,
        "reply-to": reply_to,
        "include_vars": include_vars
    }

    if not os.path.exists(os.path.dirname(storage)):
        os.makedirs(os.path.dirname(storage))

    with filelock.FileLock(current_app.config["LOCK_FILENAME"]):
        logs = _read_log(storage) + [add]
        with open(storage, "w") as file:
            file.write(json.dumps(logs))


def find(storage: str, email: str) -> bool:
    with filelock.FileLock(current_app.config["LOCK_FILENAME"]):
        for entry in _read_log(storage):
            if entry.get('include_vars', {}).get('confirm') == email:
                return True
        return False


def _read_log(storage):
    if os.path.exists(storage):
        with open(storage, "r") as file:
            return json.loads(file.read())
    else:
        return []
