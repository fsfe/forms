import copy
import json
from typing import List, Set

from fsfe_forms.common.config import CONFIGURATION_FOLDER, CONFIRMATION_EMAIL_SUBJECT, CONFIRMATION_DUPLICATE_EMAIL_SUBJECT, DEFAULT_SUBJECT_LANG, LANG_STRING_TOKEN, TEMPLATES_FOLDER
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import TemplateRenderService
import os


def _template_field(field, data: dict):
    if isinstance(field, str):
        try:
            return TemplateRenderService.render_content(field, data)
        except:
            return field
    if isinstance(field, dict):
        return {k: _template_field(v, data) for k, v in field.items()}
    return field


def _merge_field(config_field, data_field, request_data: dict):
    selected_field = data_field if config_field is None else config_field
    return _template_field(selected_field, request_data)


class TemplateContentConfig:
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content

    @classmethod
    def load_from_dict(cls, data: dict):
        filename = data.get('filename', None)
        if filename is not None:
            filename = os.path.join(TEMPLATES_FOLDER, filename)
        content = data.get('content', None)
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
    def __init__(self, name: str, required_vars: Set[str], headers: dict, plain, html):
        self.html = html
        self.plain = plain
        self.headers = headers
        self.name = name
        self.required_vars = required_vars

    @classmethod
    def load_from_dict(cls, name: str, data: dict):
        required_vars = set(data.get('required_vars', list()))
        headers = data.get('headers', dict())
        html_dict = data.get('html', None)
        plain_dict = data.get('plain', None)
        html = TemplateContentConfig.load_from_dict(html_dict) if html_dict is not None else None
        plain = TemplateContentConfig.load_from_dict(plain_dict) if plain_dict is not None else None
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
        ratelimit = data.get('ratelimit', None)
        template = data.get('template', None)
        redirect = data.get('redirect', None)
        redirect_confirmed = data.get('redirect-confirmed', None)
        confirm = data.get('confirm', None)
        confirmation_check_duplicates = data.get('confirmation-check-duplicates', False)
        store = data.get('store', None)
        include_vars = data.get('include_vars', False)
        subject = data.get('subject', None)
        reply_to = data.get('reply_to', None)
        send_to = data.get('to', None)
        send_to = list(send_to) if send_to is not None else None
        send_from = data.get('from', None)
        required_vars = set(data.get('required_vars', list()))
        headers = data.get('headers', dict())
        confirmation_from = data.get('confirmation-from', None)
        confirmation_template = data.get('confirmation-template', None)
        confirmation_duplicate_template = data.get('confirmation-duplicate-template', None)
        confirmation_subject = data.get('confirmation-subject', CONFIRMATION_EMAIL_SUBJECT)
        confirmation_duplicate_subject = data.get('confirmation-duplicate-subject', CONFIRMATION_DUPLICATE_EMAIL_SUBJECT)
        return cls(appid, ratelimit, send_from, send_to, reply_to, subject, include_vars, store,
                   confirm, confirmation_check_duplicates,
                   redirect, redirect_confirmed, template, required_vars, headers,
                   confirmation_from, confirmation_template, confirmation_duplicate_template,
                   confirmation_subject, confirmation_duplicate_subject)

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
        if merged_app_config.template is not None:
            template_config = self.get_template_config(merged_app_config.template)
            merged_app_config = merged_app_config.merge_required_vars_with_template(template_config)
        if merged_app_config.confirmation_template is not None:
            confirmation_template_config = self.get_template_config(merged_app_config.confirmation_template)
            merged_app_config = merged_app_config.merge_required_vars_with_template(confirmation_template_config)
        if merged_app_config.confirmation_duplicate_template is not None:
            confirmation_duplicate_template_config = self.get_template_config(merged_app_config.confirmation_duplicate_template)
            merged_app_config = merged_app_config.merge_required_vars_with_template(confirmation_duplicate_template_config)
        return merged_app_config

    def get_config_for_email(self, data: SendData):
        return self._get_config_for_field(data, 'template')

    def get_config_for_confirmation(self, data: SendData):
        return self._get_config_for_field(data, 'confirmation_template')

    def get_config_for_confirmation_duplicate(self, data: SendData):
        return self._get_config_for_field(data, 'confirmation_duplicate_template')

    def get_config(self, appid: str):
        configs = [c for c in self.appconfigs if c.appid.__eq__(appid)]
        if len(configs) > 0:
            return configs[0]
        else:
            return None

    def get_app_configs(self) -> List[AppConfig]:
        return list(self.appconfigs)

    def get_template_config(self, name: str):
        configs = [c for c in self.tempconfigs if c.name.__eq__(name)]
        if len(configs) > 0:
            return configs[0]
        else:
            return None

    @classmethod
    def load_from_dict(cls, applications_dict: dict, templates_dict):
        application_configs = list()
        template_configs = list()
        if applications_dict is not None:
            for appid in applications_dict:
                app_config = AppConfig.load_from_dict(str(appid), applications_dict.get(appid))
                if app_config is not None:
                    application_configs.append(app_config)
        if template_configs is not None:
            for template_name in templates_dict:
                temp_config = TemplateConfig.load_from_dict(template_name, templates_dict.get(template_name))
                if temp_config is not None:
                    template_configs.append(temp_config)
        return cls(application_configs, template_configs)

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

def load_json_dict(filename: str) -> dict:
    with open(filename) as fp:
        return json.load(fp)


configuration = Configuration.load_from_dict(load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'applications.json')),
                                             load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'templates.json')))
