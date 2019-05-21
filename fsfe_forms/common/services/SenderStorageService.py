import uuid
from fsfe_forms.common.services import StorageService
from fsfe_forms.common.models import SendData
from typing import Iterator, Tuple

SENDER_TABLE = 'sender'


def store_data(data: SendData, expire: int = None) -> uuid.UUID:
    return StorageService.create(SENDER_TABLE, data, expire)


def update_data(id: uuid.UUID, data: SendData, expire: int = None):
    StorageService.set(SENDER_TABLE, id, data, expire)


def resolve_data(id: uuid.UUID) -> SendData:
    return StorageService.get(SENDER_TABLE, id, SendData)


def remove(id: uuid.UUID):
    StorageService.remove(SENDER_TABLE, id)

def get_all() -> Tuple[str, Iterator[SendData]]:
    yield from StorageService.get_all(SENDER_TABLE, SendData)

def get_ttl(id: uuid.UUID) -> int:
    return StorageService.get_ttl(SENDER_TABLE, id)
