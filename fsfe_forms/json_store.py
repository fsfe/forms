"""Storage of (confirmed) request data in a JSON file"""

# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
# SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import time

from filelock import FileLock
from flask import current_app


def log(storage, send_from, send_to, subject, content, reply_to, include_vars) -> None:
    add = {
        "timestamp": time.time(),
        "from": send_from,
        "to": send_to,
        "subject": subject,
        "content": content,
        "reply-to": reply_to,
        "include_vars": include_vars,
    }

    if not os.path.exists(os.path.dirname(storage)):
        os.makedirs(os.path.dirname(storage))

    with FileLock(current_app.config["LOCK_FILENAME"]):
        logs = _read_log(storage) + [add]
        with open(storage, "w") as file:
            file.write(json.dumps(logs))


def find(storage: str, email: str) -> bool:
    with FileLock(current_app.config["LOCK_FILENAME"]):
        for entry in _read_log(storage):
            if entry.get("include_vars", {}).get("confirm") == email:
                return True
        return False


def _read_log(storage) -> list:
    rval: list = []
    if os.path.exists(storage):
        with open(storage) as f:
            rval = json.loads(f.read())
    return rval
