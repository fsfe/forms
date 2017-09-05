import uuid

from background.app import app
from common.config import CONFIRMATION_EMAIL_SUBJECT
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
    email_tasks[data.appid].delay(current_config.send_from, [data.confirm], current_config.confirmation_subject,
                                  content, None, current_config.headers)


@app.task(name='tasks.schedule_email')
def schedule_email(id: str):
    id = uuid.UUID(id)
    data = SenderStorageService.resolve_data(id)
    current_config = configuration.get_config_for_email(data)
    content = TemplateService.render_email(data)
    email_tasks[current_config.appid].delay(current_config.send_from, current_config.send_to, current_config.subject,
                                            content, current_config.reply_to, current_config.headers)
    if current_config.store is not None:
        store_emails.delay(current_config.store, current_config.send_from, current_config.send_to,
                           current_config.subject, content, current_config.reply_to, data.request_data)
    SenderStorageService.remove(id)


@app.task(name='tasks.store_emails')
def store_emails(storage, send_from, send_to, subject, content, reply_to, include_vars):
    DeliveryService.log(storage, send_from, send_to, subject, content, reply_to, include_vars)
