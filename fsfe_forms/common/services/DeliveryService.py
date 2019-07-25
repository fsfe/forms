import json
import filelock
import time
import os

from fsfe_forms.config import LOCK_FILENAME


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

    lock = filelock.FileLock(LOCK_FILENAME)
    logs = _read_log(storage, lock) + [add]
    logs_in_json = json.dumps(logs)
    with lock, open(storage, "w") as file:
        file.write(logs_in_json)


def find(storage: str, email: str) -> bool:
    for entry in _read_log(storage):
        if entry.get('include_vars', {}).get('confirm') == email:
            return True
    return False


def _read_log(storage, lock=filelock.FileLock(LOCK_FILENAME)):
    _create_log_file_if_not_exist(storage, lock)
    with lock, open(storage, "r") as file:
        f = file.read()
    return json.loads(f)


def _create_log_file_if_not_exist(storage, lock):
    with lock:
        if not os.path.exists(os.path.dirname(storage)):
            os.makedirs(os.path.dirname(storage))

        if not os.path.exists(storage):
            with open(storage, "w") as file:
                file.write(json.dumps([]))
