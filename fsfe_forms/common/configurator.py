import os
import copy
import json
from typing import List, Set, Any, Dict

from fsfe_forms.common.config import CONFIGURATION_FOLDER, CONFIRMATION_EMAIL_SUBJECT, CONFIRMATION_DUPLICATE_EMAIL_SUBJECT, DEFAULT_SUBJECT_LANG, LANG_STRING_TOKEN, TEMPLATES_FOLDER
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import TemplateRenderService


class TemplateContentConfig:
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content

    @classmethod
    def load_from_dict(cls, data: dict):
        filename = data.get('filename')
        if filename is not None:
            filename = os.path.join(TEMPLATES_FOLDER, filename)
        content = data.get('content')
        return cls(filename, content)

    def get_template(self, lang):
        if self.content:
            return self.content
        filename = self.get_filename(lang)
        with open(filename) as f:
            return f.read()

    def get_filename(self, lang, default_lang=DEFAULT_SUBJECT_LANG):
        if LANG_STRING_TOKEN in self.filename:
            filename = self.filename.format(lang=lang)
            if os.path.isfile(filename):
                return filename
            return self.filename.format(lang=default_lang)
        return self.filename


class TemplateConfig:
    def __init__(self, name: str, required_vars: Set[str], headers: Dict, plain, html):
        self.html = html
        self.plain = plain
        self.headers = headers
        self.name = name
        self.required_vars = required_vars

    @classmethod
    def load_from_dict(cls, name: str, data: dict):
        required_vars = set(data.get('required_vars', []))
        headers = data.get('headers', {})
        html = TemplateContentConfig.load_from_dict(data['html']) if 'html' in data else None
        plain = TemplateContentConfig.load_from_dict(data['plain']) if 'plain' in data else None
        return cls(name, required_vars, headers, plain, html)

    def get_html_template(self, lang=None):
        return self.html.get_template(lang) if self.html is not None else None

    def get_plain_template(self, lang=None):
        return self.plain.get_template(lang) if self.plain is not None else None

    def merge_config_with_send_data(self, data: SendData):
        cpy = copy.deepcopy(self)
        for field, value in cpy.headers.items():
            cpy.headers[field] = _template_field(value, data.request_data)
        return cpy


class AppConfig:
    def __init__(self, appid: str, ratelimit: int, send_from: str, send_to: List[str], reply_to: str, subject: str,
                 include_vars: bool, store: str,
                 confirm: bool, confirmation_check_duplicates: bool,
                 redirect: str, redirect_confirmed: str, template,
                 required_vars: Set[str], headers: dict,
                 confirmation_from: str, confirmation_template: str, confirmation_duplicate_template: str,
                 confirmation_subject: str, confirmation_duplicate_subject: str):
        self.confirmation_from = confirmation_from
        self.confirmation_template = confirmation_template
        self.confirmation_duplicate_template = confirmation_duplicate_template
        self.confirmation_subject = confirmation_subject
        self.confirmation_duplicate_subject = confirmation_duplicate_subject
        self.headers = headers
        self.appid = appid
        self.ratelimit = ratelimit
        self.template = template
        self.redirect = redirect
        self.redirect_confirmed = redirect_confirmed
        self.confirm = confirm
        self.confirmation_check_duplicates = confirmation_check_duplicates
        self.store = store
        self.include_vars = include_vars
        self.subject = subject
        self.reply_to = reply_to
        self.send_to = send_to
        self.send_from = send_from
        self.required_vars = required_vars

    @classmethod
    def load_from_dict(cls, appid: str, data: dict):
        args = {
            'ratelimit': data.get('ratelimit'),
            'template': data.get('template'),
            'redirect': data.get('redirect'),
            'redirect_confirmed': data.get('redirect-confirmed'),
            'confirm': data.get('confirm'),
            'confirmation_check_duplicates': data.get('confirmation-check-duplicates', False),
            'store': data.get('store'),
            'include_vars': data.get('include_vars', False),
            'subject': data.get('subject'),
            'reply_to': data.get('reply_to'),
            'send_to': list(data['to']) if 'to' in data else None,
            'send_from': data.get('from'),
            'required_vars': set(data.get('required_vars', [])),
            'headers': data.get('headers', {}),
            'confirmation_from': data.get('confirmation-from'),
            'confirmation_template': data.get('confirmation-template'),
            'confirmation_duplicate_template': data.get('confirmation-duplicate-template'),
            'confirmation_subject': data.get('confirmation-subject', CONFIRMATION_EMAIL_SUBJECT),
            'confirmation_duplicate_subject': data.get('confirmation-duplicate-subject', CONFIRMATION_DUPLICATE_EMAIL_SUBJECT)
        }
        return cls(appid, **args)

    def merge_config_with_send_data(self, data: SendData):
        cpy = copy.deepcopy(self)
        cpy.send_from = _merge_field(self.send_from, data.send_from, data.request_data)
        cpy.send_to = _merge_field(self.send_to, data.send_to, data.request_data)
        cpy.reply_to = _merge_field(self.reply_to, data.reply_to, data.request_data)
        cpy.subject = _merge_field(self.subject, data.subject, data.request_data)
        cpy.template = _merge_field(self.template, data.template, data.request_data)
        cpy.confirmation_subject = _template_field(self.confirmation_subject, data.request_data)
        for field, value in cpy.headers.items():
            cpy.headers[field] = _template_field(value, data.request_data)
        return cpy

    def merge_required_vars_with_template(self, data: TemplateConfig):
        cpy = copy.deepcopy(self)
        cpy.required_vars = cpy.required_vars.union(data.required_vars)
        return cpy

    def merge_with_template_config(self, data: TemplateConfig):
        cpy = copy.deepcopy(self)
        cpy.required_vars = cpy.required_vars.union(data.required_vars)
        for field in data.headers:
            if field in cpy.headers:
                continue
            cpy.headers[field] = data.headers[field]
        return cpy


class Configuration:
    def __init__(self, appconfigs: List[AppConfig], tempconfigs: List[TemplateConfig]):
        self.appconfigs = appconfigs
        self.tempconfigs = tempconfigs

    def get_config_merged_with_data(self, data: SendData):
        config = self.get_config(data.appid)
        if config is None:
            return None
        merged_app_config = config.merge_config_with_send_data(data)
        return merged_app_config

    def get_config_for_validation(self, data: SendData):
        merged_app_config = self.get_config_merged_with_data(data)
        if merged_app_config is None:
            return None
        merged_app_config = self._merged_app_config(merged_app_config, 'template')
        merged_app_config = self._merged_app_config(merged_app_config, 'confirmation_template')
        merged_app_config = self._merged_app_config(merged_app_config, 'confirmation_duplicate_template')
        return merged_app_config

    def get_config_for_email(self, data: SendData):
        return self._get_config_for_field(data, 'template')

    def get_config_for_confirmation(self, data: SendData):
        return self._get_config_for_field(data, 'confirmation_template')

    def get_config_for_confirmation_duplicate(self, data: SendData):
        return self._get_config_for_field(data, 'confirmation_duplicate_template')

    def get_config(self, appid: str):
        configs = filter(lambda c: c.appid.__eq__(appid), self.appconfigs)
        return next(configs, None)

    def get_template_config(self, name: str):
        configs = filter(lambda c: c.name.__eq__(name), self.tempconfigs)
        return next(configs, None)

    @classmethod
    def load_from_dict(cls, applications_dict: dict, templates_dict):
        _load_conf = lambda obj_conf, confs: _load_from_dict(obj_conf, confs) if confs else []
        application_configs = _load_conf(AppConfig, applications_dict)
        template_configs = _load_conf(TemplateConfig, templates_dict)
        return cls(application_configs, template_configs)

    def _merged_app_config(self, merged_app_config, template_name):
        template = getattr(merged_app_config, template_name)
        if template is not None:
            template_config = self.get_template_config(template)
            merged_app_config = merged_app_config.merge_required_vars_with_template(template_config)
        return merged_app_config

    def _get_config_for_field(self, data: SendData, field: str):
        merged_app_config = self.get_config_merged_with_data(data)
        if merged_app_config is None:
            return None
        merged_app_config_attr = getattr(merged_app_config, field)
        if merged_app_config_attr is not None:
            template_config = self.get_template_config(merged_app_config_attr)
            merged_template_config = template_config.merge_config_with_send_data(data)
            merged_app_config = merged_app_config.merge_with_template_config(merged_template_config)
        return merged_app_config


def _merge_field(config_field, data_field, request_data: dict):
    selected_field = data_field if config_field is None else config_field
    return _template_field(selected_field, request_data)


def _template_field(field, data: dict):
    if isinstance(field, str):
        try:
            return TemplateRenderService.render_content(field, data)
        except:
            return field
    if isinstance(field, dict):
        return {k: _template_field(v, data) for k, v in field.items()}
    return field


def load_json_dict(filename: str) -> dict:
    with open(filename) as fp:
        return json.load(fp)


def _load_from_dict(config_cls: object, confs: Dict[str, Any]) -> List[object]:
    # Load configuration for each application
    configs = map(lambda c: config_cls.load_from_dict(str(c), confs.get(c)), confs)
    # Remove empty configuration
    return list(filter(None, configs))


configuration = Configuration.load_from_dict(load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'applications.json')),
                                             load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'templates.json')))
