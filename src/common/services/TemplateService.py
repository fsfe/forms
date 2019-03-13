import os
import re
from urllib.parse import urljoin
from common.configurator import configuration
from common.models import SendData
from common.services import TemplateRenderService

from common.config import DEFAULT_SUBJECT_LANG, CONFIRMATION_MULTILANG_TEMPLATE


def render_confirmation(id, data: SendData):
    final_config = configuration.get_config_for_confirmation(data)
    email_content = render_email(data)
    confirmation_url = _generate_confirmation_url(data.url, id)
    if final_config.confirmation_template is not None:
        if final_config.include_vars:
            request_data = data.request_data
        else:
            request_data = dict()
        request_data['content'] = email_content
        request_data['confirmation_url'] = confirmation_url
        if final_config.confirmation_template is not None:
            template_config = configuration.get_template_config(final_config.confirmation_template)
            template_html_content = template_config.get_html_template()
            template_plain_content = template_config.get_plain_template()
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
    else:
        filename = CONFIRMATION_MULTILANG_TEMPLATE.format(lang=data.lang)
        if not os.path.isfile(filename):
            filename = CONFIRMATION_MULTILANG_TEMPLATE.format(lang=DEFAULT_SUBJECT_LANG)
        with open(filename) as f:
            content = f.read()
            return TemplateRenderService.render_content(content, {
                'content': email_content,
                'confirmation_url': confirmation_url
            })


def render_email(data: SendData):
    final_config = configuration.get_config_for_email(data)
    if final_config.include_vars:
        request_data = data.request_data
    else:
        request_data = dict()
    if final_config.template is not None:
        template_config = configuration.get_template_config(final_config.template)
        template_html_content = template_config.get_html_template(data.lang)
        template_plain_content = template_config.get_plain_template(data.lang)
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
