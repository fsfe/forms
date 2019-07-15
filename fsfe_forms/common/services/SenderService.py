import uuid
from typing import Optional

from fsfe_forms.background.tasks import schedule_confirmation, schedule_email
from fsfe_forms.common import exceptions
from fsfe_forms.common.config import CONFIRMATION_EXPIRATION_SECS
from fsfe_forms.common.configurator import AppConfig, configuration
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import SenderStorageService


def validate_and_send_email(data: SendData):
    config = configuration.get_config(data)
    if config is None:
        raise exceptions.NotFound('Configuration not found for this AppId')
    if config.send_from is None:
        raise exceptions.BadRequest('\"From\" is required')
    if config.send_to is None or not config.send_to:
        raise exceptions.BadRequest('\"To\" is required')
    if config.subject is None:
        raise exceptions.BadRequest('\"Subject\" is required')
    if config.template is None:
        raise exceptions.BadRequest('\"Template\" is required')
    for field in config.required_vars:
        if field not in data.request_data:
            raise exceptions.BadRequest('\"%s\" is required' % field)

    if config.confirm:
        if data.confirm is None:
            raise exceptions.BadRequest('\"Confirm\" address is required')
        id = SenderStorageService.store_data(data, CONFIRMATION_EXPIRATION_SECS)
        schedule_confirmation(id, data, config)
    else:
        id = SenderStorageService.store_data(data)
        schedule_email(id, data, config)
    return config


def confirm_email(id: str) -> Optional[AppConfig]:
    id = uuid.UUID(id)
    data = SenderStorageService.resolve_data(id)
    if data is None:
        raise exceptions.NotFound('Confirmation ID is Not Found')
    config = configuration.get_config(data)
    if config is None:
        raise exceptions.NotFound('Configuration not found for this AppId')
    if not data.confirmed:
        data.confirmed = True
        SenderStorageService.update_data(id, data)
        schedule_email(id, data, config)
    return config
