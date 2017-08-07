import json
import uuid

import redis

from common.config import REDIS_HOST, REDIS_PORT
from common.models import Serializable

storage = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def set(table: str, id: uuid.UUID, data: Serializable, expire: int = None):
    key = _sanitize_key(table, id)
    json_data = data.toJSON()
    storage.set(key, json_data, expire)


def create(table: str, data: Serializable, expire: int = None) -> uuid.UUID:
    id = uuid.uuid4()
    set(table, id, data, expire)
    return id


def get(table: str, id: uuid.UUID, type=None):
    key = _sanitize_key(table, id)
    str_data = storage.get(key)
    if str_data is None:
        return None
    if type is not None and issubclass(type, Serializable):
        data = type.fromJSON(str_data)
    else:
        data = json.loads(str_data)
    return data


def remove(table: str, id: uuid.UUID):
    key = _sanitize_key(table, id)
    storage.delete(key)


def get_queue_tasks_count(queue_name: str):
    return int(storage.llen(queue_name))


def _sanitize_key(table: str, key: uuid.UUID) -> str:
    return 'datastorage.%s:%s' % (table, key)
