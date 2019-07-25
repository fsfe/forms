import uuid
from typing import Optional

from flask import abort

from fsfe_forms.background.tasks import schedule_confirmation, schedule_email
from fsfe_forms.common.config import CONFIRMATION_EXPIRATION_SECS
from fsfe_forms.common.configurator import AppConfig, configuration
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import SenderStorageService


def validate_and_send_email(data: SendData):
    config = configuration.get_config(data)
    if config is None:
        abort(404, 'Configuration not found for this AppId')
    if config.send_from is None:
        abort(400, '\"From\" is required')
    if config.send_to is None or not config.send_to:
        abort(400, '\"To\" is required')
    if config.subject is None:
        abort(400, '\"Subject\" is required')
    if config.template is None:
        abort(400, '\"Template\" is required')
    for field in config.required_vars:
        if field not in data.request_data:
            raise abort(400, '\"%s\" is required' % field)

    if config.confirm:
        if data.confirm is None:
            abort(400, '\"Confirm\" address is required')
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
        abort(404, 'Confirmation ID is Not Found')
    config = configuration.get_config(data)
    if config is None:
        abort(404, 'Configuration not found for this AppId')
    if not data.confirmed:
        data.confirmed = True
        SenderStorageService.update_data(id, data)
        schedule_email(id, data, config)
    return config
