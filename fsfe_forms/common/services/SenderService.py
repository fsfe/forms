import uuid

from flask import abort, current_app

from fsfe_forms.background.tasks import schedule_confirmation, schedule_email
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import SenderStorageService
from fsfe_forms.config import CONFIRMATION_EXPIRATION_SECS


def validate_and_send_email(data: SendData) -> str:
    config = current_app.app_configs.get(data.appid)
    if config is None:
        abort(404, 'Configuration not found for this AppId')
    for field in config['required_vars']:
        if field not in data.request_data:
            raise abort(400, '\"%s\" is required' % field)

    if 'confirm' in config:
        if data.confirm is None:
            abort(400, '\"Confirm\" address is required')
        id = SenderStorageService.store_data(data, CONFIRMATION_EXPIRATION_SECS)
        return schedule_confirmation(id, data, config)
    else:
        id = SenderStorageService.store_data(data)
        return schedule_email(id, data, config)


def confirm_email(id: str) -> str:
    id = uuid.UUID(id)
    data = SenderStorageService.resolve_data(id)
    if data is None:
        abort(404, 'Confirmation ID is Not Found')
    config = current_app.app_configs.get(data.appid)
    if config is None:
        abort(404, 'Configuration not found for this AppId')
    if not data.confirmed:
        data.confirmed = True
        SenderStorageService.update_data(id, data)
    return schedule_email(id, data, config)
