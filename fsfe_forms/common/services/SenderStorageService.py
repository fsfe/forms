import uuid
from typing import Iterator, Tuple
from fsfe_forms.common.services import StorageService
from fsfe_forms.common.models import SendData
from fsfe_forms.config import SENDER_TABLE


def store_data(data: SendData, expire: int = None) -> uuid.UUID:
    # Check for an unconfirmed previous registration, and if found, update and
    # reuse that one and discard the new registration
    for (key, old_data) in StorageService.get_all(SENDER_TABLE, SendData):
        if old_data.request_data.get('confirm') == data.request_data.get('confirm') \
                and old_data.request_data.get('appid') == data.request_data.get('appid'):
            ttl = StorageService.get_ttl(SENDER_TABLE, key)
            StorageService.set(SENDER_TABLE, key, data, ttl)
        return uuid.UUID(key)
    else:
        return StorageService.create(SENDER_TABLE, data, expire)


def resolve_data(id: uuid.UUID) -> SendData:
    return StorageService.get(SENDER_TABLE, id, SendData)


def remove(id: uuid.UUID):
    StorageService.remove(SENDER_TABLE, id)


