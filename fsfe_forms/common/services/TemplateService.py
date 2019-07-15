import os
from typing import Union
from urllib.parse import urljoin
from fsfe_forms.common.configurator import AppConfig
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import TemplateRenderService

from fsfe_forms.common.config import DEFAULT_SUBJECT_LANG, CONFIRMATION_MULTILANG_TEMPLATE, CONFIRMATION_DUPLICATE_MULTILANG_TEMPLATE


def render_confirmation_duplicate(config: AppConfig, id, data: SendData):
    template, is_generic_template = _get_render_template(config.confirmation_duplicate_template, CONFIRMATION_DUPLICATE_MULTILANG_TEMPLATE)
    return _generic_render(config, data, template, is_generic_template)


def render_confirmation(config: AppConfig, id, data: SendData):
    request_data = {'confirmation_url': _generate_confirmation_url(data.url, id)}
    template, is_generic_template = _get_render_template(config.confirmation_template, CONFIRMATION_MULTILANG_TEMPLATE)
    return _generic_render(config, data, template, is_generic_template, request_data)


def render_email(config: AppConfig, data: SendData):
    return _render_custom_template(data, config.template)


def _generate_confirmation_url(url, id):
    return urljoin(url, 'confirm?id=%s' % id)


def _get_render_template(custom_template: Union[str, None], generic_template: str):
    is_generic_template = bool(custom_template)
    template = custom_template if is_generic_template else generic_template
    return template, is_generic_template


def _generic_render(config: AppConfig, data: SendData, template: str, custom_template: bool, request_data={}):
    _request_data = {
        'content': render_email(config, data),
        **request_data
    }
    if custom_template:
        return _render_custom_template(data, template, _request_data)
    return _render_generic_template(data, template, _request_data)


def _render_custom_template(data, template, request_data={}):
    _request_data = data.request_data
    _request_data.update(request_data)

    template_html_content = template.get_html_template()
    template_plain_content = template.get_plain_template()

    _render_content = lambda c: TemplateRenderService.render_content(c, _request_data)
    _render_content_if_exist = lambda c: _render_content(c) if c else None

    return {
        "html": _render_content_if_exist(template_html_content),
        "plain": _render_content_if_exist(template_plain_content)
    }


def _render_generic_template(data, generic_template, request_data):
    filename = generic_template.format(lang=data.lang)
    if not os.path.isfile(filename):
        filename = generic_template.format(lang=DEFAULT_SUBJECT_LANG)

    with open(filename) as f:
        content = f.read()
        return TemplateRenderService.render_content(content, request_data)
