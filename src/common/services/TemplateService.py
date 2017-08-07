from urllib.parse import urljoin
from bottle import jinja2_template as template
from common.configurator import configuration
from common.models import SendData

CONFIRMATION_TEMPLATE = 'common/templates/confirmation.html'


def render_confirmation(id, data: SendData):
    return template(CONFIRMATION_TEMPLATE, confirmation_url=_generate_confirmation_url(data.url, id))


def render_email(data: SendData):
    final_config = configuration.get_config(data.appid).merge_config_with_send_data(data)
    if final_config.template is not None:
        template_config = configuration.get_template_config(final_config.template)
        template_content = template_config.get_template()
    elif final_config.content is not None:
        template_content = final_config.content
    else:
        return None
    if final_config.include_vars:
        return template(template_content, data.request_data)
    return template(template_content, dict())


def _generate_confirmation_url(url, id):
    return urljoin(url, 'confirm?id=%s' % id)
