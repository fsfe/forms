import uuid
from common.services import StorageService
from common.models import SendData

SENDER_TABLE = 'sender'


def store_data(data: SendData, expire: int = None) -> uuid.UUID:
    return StorageService.create(SENDER_TABLE, data, expire)


def update_data(id: uuid.UUID, data: SendData, expire: int = None):
    StorageService.set(SENDER_TABLE, id, data, expire)


def resolve_data(id: uuid.UUID) -> SendData:
    return StorageService.get(SENDER_TABLE, id, SendData)


def remove(id: uuid.UUID):
    StorageService.remove(SENDER_TABLE, id)
