import os
from typing import Union
from urllib.parse import urljoin
from fsfe_forms.common.configurator import configuration
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import TemplateRenderService

from fsfe_forms.common.config import DEFAULT_SUBJECT_LANG, CONFIRMATION_MULTILANG_TEMPLATE, CONFIRMATION_DUPLICATE_MULTILANG_TEMPLATE


def render_confirmation_duplicate(id, data: SendData):
    final_config = configuration.get_config_for_confirmation_duplicate(data)
    template, is_generic_template = _get_render_template(final_config.confirmation_duplicate_template, CONFIRMATION_DUPLICATE_MULTILANG_TEMPLATE)
    return _generic_render(id, data, template, final_config.include_vars, is_generic_template)


def render_confirmation(id, data: SendData):
    final_config = configuration.get_config_for_confirmation(data)
    request_data = {'confirmation_url': _generate_confirmation_url(data.url, id)}
    template, is_generic_template = _get_render_template(final_config.confirmation_template, CONFIRMATION_MULTILANG_TEMPLATE)
    return _generic_render(id, data, template, final_config.include_vars, is_generic_template, request_data)


def render_email(data: SendData):
    final_config = configuration.get_config_for_email(data)
    template = final_config.template
    include_vars = final_config.include_vars
    return _render_custom_template(data, template, include_vars)


def _generate_confirmation_url(url, id):
    return urljoin(url, 'confirm?id=%s' % id)


def _get_render_template(custom_template: Union[str, None], generic_template: str):
    is_generic_template = bool(custom_template)
    template = custom_template if is_generic_template else generic_template
    return template, is_generic_template


def _generic_render(id, data: SendData, template: str, include_vars: bool, custom_template: bool, request_data={}):
    _request_data = {
        'content': render_email(data),
        **request_data
    }
    if custom_template:
        return _render_custom_template(data, template, include_vars, _request_data)
    return _render_generic_template(data, template, _request_data)


def _render_custom_template(data, template, include_vars, request_data={}):
    _request_data = data.request_data if include_vars else dict()
    _request_data.update(request_data)

    template_config = configuration.get_template_config(template)
    template_html_content = template_config.get_html_template()
    template_plain_content = template_config.get_plain_template()

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
