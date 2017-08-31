from urllib.parse import urljoin
from common.configurator import configuration
from common.models import SendData
from common.services import TemplateRenderService

CONFIRMATION_TEMPLATE = 'common/templates/confirmation.html'


def render_confirmation(id, data: SendData):
    with open(CONFIRMATION_TEMPLATE) as f:
        content = f.read()
    return TemplateRenderService.render_content(content, {
        'content': render_email(data),
        'confirmation_url': _generate_confirmation_url(data.url, id)
    })


def render_email(data: SendData):
    final_config = configuration.get_config_merged_with_data(data.appid, data)
    if final_config.include_vars:
        request_data = data.request_data
    else:
        request_data = dict()
    if final_config.template is not None:
        template_config = configuration.get_template_config(final_config.template)
        template_html_content = template_config.get_html_template()
        template_plain_content = template_config.get_plain_template()
    elif final_config.content is not None:
        return TemplateRenderService.render_content(final_config.content, request_data)
    else:
        return None
    html = TemplateRenderService.render_content(template_html_content,
                                                request_data) if template_html_content is not None else None
    plain = TemplateRenderService.render_content(template_plain_content,
                                                 request_data) if template_plain_content is not None else None
    return {
        "html": html,
        "plain": plain
    }


def _generate_confirmation_url(url, id):
    return urljoin(url, 'confirm?id=%s' % id)
