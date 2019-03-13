import uuid

from typing import Optional, Union
from background.app import app
from common.config import DEFAULT_SUBJECT_LANG
from common.configurator import configuration
from common.services import DeliveryService, SenderStorageService, TemplateService

email_tasks = dict()


def send_email(send_from, send_to, subject, content, reply_to, headers):
    DeliveryService.send(send_from, send_to, subject, content, reply_to, headers)


for config in configuration.get_app_configs():
    if config.ratelimit is not None:
        email_task = app.task(send_email, name='send_email:%s' % config.appid, rate_limit='%s/h' % config.ratelimit)
    else:
        email_task = app.task(send_email, name='send_email:%s' % config.appid)
    email_tasks[config.appid] = email_task


@app.task(name='tasks.schedule_confirmation')
def schedule_confirmation(id: str):
    id = uuid.UUID(id)
    data = SenderStorageService.resolve_data(id)
    current_config = configuration.get_config_for_confirmation(data)
    content = TemplateService.render_confirmation(id, data)
    subject = get_subject(current_config.confirmation_subject, data.lang)
    email_tasks[data.appid].delay(current_config.confirmation_from, [data.confirm], subject,
                                  content, None, None)


@app.task(name='tasks.schedule_email')
def schedule_email(id: str):
    id = uuid.UUID(id)
    data = SenderStorageService.resolve_data(id)
    current_config = configuration.get_config_for_email(data)
    content = TemplateService.render_email(data)
    subject = get_subject(current_config.subject, data.lang)
    email_tasks[current_config.appid].delay(current_config.send_from, current_config.send_to, subject,
                                            content, current_config.reply_to, current_config.headers)
    if current_config.store is not None:
        store_emails.delay(current_config.store, current_config.send_from, current_config.send_to,
                           subject, content, current_config.reply_to, data.request_data)
    SenderStorageService.remove(id)


@app.task(name='tasks.store_emails')
def store_emails(storage, send_from, send_to, subject, content, reply_to, include_vars):
    DeliveryService.log(storage, send_from, send_to, subject, content, reply_to, include_vars)

def get_subject(subject: Union[str, dict], lang: Union[None, str], default_lang: Union[None, str] = DEFAULT_SUBJECT_LANG):
    if isinstance(subject, str):
        return subject
    if isinstance(subject, dict):
        _lang = lang if lang in subject else default_lang
        return subject[_lang]
    raise ValueError('Subject should be a string or a dict')
