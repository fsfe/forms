import uuid

from flask import url_for

from fsfe_forms.common.services import DeliveryService
from fsfe_forms.common.models import SendData
from fsfe_forms.email import send_email


def schedule_confirmation(id: uuid.UUID, data: SendData, current_config: dict):
    '''
    Send a confirmation email to a user
    A check is done on previous emails sent (in case of spam or email lost for example)
    If a confirmation email was sent, it's data are updates with new email data and a new confirmation email is sent again with the same url link
    '''
    user_email = data.request_data.get('confirm')

    # Optionally, check for a confirmed previous registration, and if found,
    # refuse the duplicate
    if 'duplicate' in current_config and DeliveryService.find(current_config['store'], user_email):
        send_email(
                template=current_config['duplicate']['email'],
                **data.request_data)
        return current_config['duplicate']['redirect']
    else:
        send_email(
                template=current_config['register']['email'],
                confirmation_url=url_for('confirm', _external=True, id=id),
                **data.request_data)
        return current_config['register']['redirect']


def schedule_email(data: SendData, current_config: dict):
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
    return current_config[action]['redirect']
