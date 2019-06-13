import uuid

from typing import Optional, Union
from fsfe_forms.common import exceptions
from fsfe_forms.common.config import DEFAULT_SUBJECT_LANG
from fsfe_forms.common.configurator import configuration, AppConfig
from fsfe_forms.common.services import DeliveryService, SenderStorageService, TemplateService
from fsfe_forms.common.models import SendData


def extract_data_and_config(func):
    '''
    Extract data and configuration from a ID
    ID can come from a previous API call or generate during the API flow of a request
    This ID map a application configuration (AppId) and user request
    '''
    def wrapper(id: uuid.UUID):
        data = SenderStorageService.resolve_data(id)
        if data:
            current_config = configuration.get_config_for_email(data)
            if current_config:
                return func(id, data, current_config)
        print(f'Error with id "{id}" with data equal to "{data}"')
        raise exceptions.NotFound('Confirmation ID is Not Found')
    return wrapper


@extract_data_and_config
def schedule_confirmation(id: uuid.UUID, data: SendData, current_config: AppConfig):
    '''
    Send a confirmation email to a user
    A check is done on previous emails sent (in case of spam or email lost for example)
    If a confirmation email was sent, it's data are updates with new email data and a new confirmation email is sent again with the same url link
    '''
    user_email = data.request_data.get('confirm')
    previous_task_id = _get_previous_task_id(id, data.appid, user_email)
    if previous_task_id:
        ttl = SenderStorageService.get_ttl(previous_task_id)
        SenderStorageService.update_data(previous_task_id, data, ttl)
        SenderStorageService.remove(id)
        id = previous_task_id
    subject, content = _get_email_subject_and_content(current_config, user_email, data, id)
    DeliveryService.send(current_config.confirmation_from, [data.confirm], subject, content, None, None)


@extract_data_and_config
def schedule_email(id: uuid.UUID, data: SendData, current_config: AppConfig):
    '''
    Generate a email from configuration and user data then send it
    When sent, email is log and user unique ID is remove
    '''
    content = TemplateService.render_email(data)
    subject = _get_subject(current_config.subject, data.lang)
    DeliveryService.send(current_config.send_from, current_config.send_to, subject,
                         content, current_config.reply_to, current_config.headers)
    if current_config.store is not None:
        DeliveryService.log(current_config.store, current_config.send_from, current_config.send_to,
                            subject, content, current_config.reply_to, data.request_data)
    SenderStorageService.remove(id)


def _get_email_subject_and_content(current_config, user_email, data, task_id):
    have_to_check_duplicates = current_config.confirmation_check_duplicates

    if have_to_check_duplicates and _has_signed_open_letter(current_config.store, user_email):
        config_subject = current_config.confirmation_duplicate_subject
        content = TemplateService.render_confirmation_duplicate
    else:
        config_subject = current_config.confirmation_subject
        content = TemplateService.render_confirmation

    return _get_subject(config_subject, data.lang), content(task_id, data)


def _has_signed_open_letter(storage: str, email: str) -> bool:
    logs = DeliveryService.read_log(storage)
    logs_with_same_email = filter(lambda l: l.get('include_vars', {}).get('confirm') == email, logs)
    exist = next(logs_with_same_email, None)
    return True if exist else False


def _get_subject(subject: Union[str, dict], lang: Union[None, str], default_lang: Union[None, str] = DEFAULT_SUBJECT_LANG):
    if isinstance(subject, str):
        return subject
    if isinstance(subject, dict):
        _lang = lang if lang in subject else default_lang
        return subject[_lang]
    raise ValueError('Subject should be a string or a dict')


def _get_previous_task_id(id: uuid.UUID, appid: str, email: str) -> uuid.UUID:
    previous_tasks = SenderStorageService.get_all()
    previous_tasks_with_same_email = filter(lambda d: d[1].request_data.get('confirm') == email, previous_tasks)
    previous_tasks_without_same_id = filter(lambda d: uuid.UUID(d[0]) != id, previous_tasks_with_same_email)
    previous_tasks_with_same_appid = filter(lambda d: d[1].appid == appid, previous_tasks_without_same_id)
    previous_tasks = next(previous_tasks_with_same_appid, None)
    return uuid.UUID(previous_tasks[0]) if previous_tasks else None

