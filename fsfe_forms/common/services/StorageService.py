import json
import uuid

import redis

from fsfe_forms.common.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from fsfe_forms.common.models import Serializable

storage = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)


def set(table: str, id: uuid.UUID, data: Serializable, expire: int = None):
    key = _sanitize_key(table, id)
    json_data = data.toJSON()
    binary_data = json_data.encode('utf-8')
    storage.set(key, binary_data, expire)


def create(table: str, data: Serializable, expire: int = None) -> uuid.UUID:
    id = uuid.uuid4()
    set(table, id, data, expire)
    return id


def get(table: str, id: uuid.UUID, type=None):
    key = _sanitize_key(table, id)
    binary_data = storage.get(key)
    if binary_data is None:
        return None
    str_data = binary_data.decode('utf-8')
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


def get_all(table: str, type=None):
    key = storage.keys(_sanitize_key(table, '*'))
    for k in key:
        binary_data = storage.get(k)
        str_data = binary_data.decode('utf-8')
        if type is not None and issubclass(type, Serializable):
            data = type.fromJSON(str_data)
        else:
            data = json.loads(str_data)
        _key = k.decode("utf-8").split(':')[-1]
        yield (_key, data)


def get_ttl(table: str, id: uuid.UUID):
    key = _sanitize_key(table, id)
    return storage.ttl(key)


def _sanitize_key(table: str, key: uuid.UUID) -> str:
    return 'datastorage.%s:%s' % (table, key)
