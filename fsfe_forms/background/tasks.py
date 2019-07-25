import uuid
from urllib.parse import urljoin

from fsfe_forms.common.services import DeliveryService, SenderStorageService
from fsfe_forms.common.models import SendData
from fsfe_forms.email import send_email


def schedule_confirmation(id: uuid.UUID, data: SendData, current_config: dict):
    '''
    Send a confirmation email to a user
    A check is done on previous emails sent (in case of spam or email lost for example)
    If a confirmation email was sent, it's data are updates with new email data and a new confirmation email is sent again with the same url link
    '''
    user_email = data.request_data.get('confirm')

    # Check for an unconfirmed previous registration, and if found, update and
    # reuse that one and discard the new registration
    previous_task_id = _get_previous_task_id(id, data.appid, user_email)
    if previous_task_id:
        ttl = SenderStorageService.get_ttl(previous_task_id)
        SenderStorageService.update_data(previous_task_id, data, ttl)
        SenderStorageService.remove(id)
        id = previous_task_id

    # Optionally, check for a confirmed previous registration, and if found,
    # refuse the duplicate
    if 'duplicate' in current_config and _has_signed_open_letter(current_config['store'], user_email):
        send_email(
                template=current_config['duplicate']['email'],
                **data.request_data)
        return current_config['duplicate']['redirect']
    else:
        send_email(
                template=current_config['register']['email'],
                confirmation_url=urljoin(data.url, 'confirm?id=%s' % id),
                **data.request_data)
        return current_config['register']['redirect']


def schedule_email(id: uuid.UUID, data: SendData, current_config: dict):
    '''
    Generate a email from configuration and user data then send it
    When sent, email is log and user unique ID is remove
    '''
    if 'confirm' in current_config:
        action = 'confirm'
    else:
        action = 'register'
    message = send_email(
            template=current_config[action]['email'],
            **data.request_data)
    if 'store' in current_config:
        DeliveryService.log(
                current_config['store'],
                message['From'],
                [message['To']],
                message['Subject'],
                message.get_content(),
                message['Reply-To'],
                data.request_data)
    SenderStorageService.remove(id)
    return current_config[action]['redirect']


def _has_signed_open_letter(storage: str, email: str) -> bool:
    logs = DeliveryService.read_log(storage)
    logs_with_same_email = filter(lambda l: l.get('include_vars', {}).get('confirm') == email, logs)
    exist = next(logs_with_same_email, None)
    return True if exist else False


def _get_previous_task_id(id: uuid.UUID, appid: str, email: str) -> uuid.UUID:
    previous_tasks = SenderStorageService.get_all()
    previous_tasks_with_same_email = filter(lambda d: d[1].request_data.get('confirm') == email, previous_tasks)
    previous_tasks_without_same_id = filter(lambda d: uuid.UUID(d[0]) != id, previous_tasks_with_same_email)
    previous_tasks_with_same_appid = filter(lambda d: d[1].appid == appid, previous_tasks_without_same_id)
    previous_tasks = next(previous_tasks_with_same_appid, None)
    return uuid.UUID(previous_tasks[0]) if previous_tasks else None
