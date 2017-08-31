import copy
import json
from typing import List, Set
from common.models import SendData
from common.services import TemplateRenderService
import os

CONFIGURATION_FOLDER = "configuration"
TEMPLATES_FOLDER = "configuration/templates"


def _template_field(field, data: dict):
    if isinstance(field, str):
        try:
            return TemplateRenderService.render_content(field, data)
        except:
            return field
    return field


def _merge_field(config_field, data_field, request_data: dict):
    selected_field = data_field if config_field is None else config_field
    return _template_field(selected_field, request_data)


class TemplateContentConfig:
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        self._contents = None

    @classmethod
    def load_from_dict(cls, data: dict):
        filename = data.get('filename', None)
        if filename is not None:
            filename = os.path.join(TEMPLATES_FOLDER, filename)
        content = data.get('content', None)
        return cls(filename, content)

    def get_template(self):
        if self._contents is None:
            if self.content is not None:
                self._contents = self.content
            elif self.filename is not None:
                with open(self.filename) as f:
                    self._contents = f.read()
        return self._contents


class TemplateConfig:
    def __init__(self, name: str, required_vars: Set[str], headers: dict, plain, html):
        self.html = html
        self.plain = plain
        self.headers = headers
        self.name = name
        self.required_vars = required_vars
        self._contents = None

    @classmethod
    def load_from_dict(cls, name: str, data: dict):
        required_vars = set(data.get('required_vars', list()))
        headers = data.get('headers', dict())
        html_dict = data.get('html', None)
        plain_dict = data.get('plain', None)
        html = TemplateContentConfig.load_from_dict(html_dict) if html_dict is not None else None
        plain = TemplateContentConfig.load_from_dict(plain_dict) if plain_dict is not None else None
        return cls(name, required_vars, headers, plain, html)

    def get_html_template(self):
        return self.html.get_template() if self.html is not None else None

    def get_plain_template(self):
        return self.plain.get_template() if self.plain is not None else None

    def merge_config_with_send_data(self, data: SendData):
        cpy = copy.deepcopy(self)
        for field, value in cpy.headers.items():
            cpy.headers[field] = _template_field(value, data.request_data)
        return cpy


class AppConfig:
    def __init__(self, appid: str, ratelimit: int, send_from: str, send_to: List[str], reply_to: str, subject: str,
                 content: str, include_vars: bool, store: str, confirm: bool, redirect: str, template,
                 required_vars: Set[str], headers: dict):
        self.headers = headers
        self.appid = appid
        self.ratelimit = ratelimit
        self.template = template
        self.redirect = redirect
        self.confirm = confirm
        self.store = store
        self.include_vars = include_vars
        self.content = content
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
        confirm = data.get('confirm', None)
        store = data.get('store', None)
        include_vars = data.get('include_vars', False)
        content = data.get('content', None)
        subject = data.get('subject', None)
        reply_to = data.get('reply_to', None)
        send_to = data.get('to', None)
        send_to = list(send_to) if send_to is not None else None
        send_from = data.get('from', None)
        required_vars = set(data.get('required_vars', list()))
        headers = data.get('headers', dict())
        return cls(appid, ratelimit, send_from, send_to, reply_to, subject, content, include_vars, store, confirm,
                   redirect, template, required_vars, headers)

    def merge_config_with_send_data(self, data: SendData):
        cpy = copy.deepcopy(self)
        cpy.send_from = _merge_field(self.send_from, data.send_from, data.request_data)
        cpy.send_to = _merge_field(self.send_to, data.send_to, data.request_data)
        cpy.reply_to = _merge_field(self.reply_to, data.reply_to, data.request_data)
        cpy.subject = _merge_field(self.subject, data.subject, data.request_data)
        cpy.content = _merge_field(self.content, data.content, data.request_data)
        cpy.template = _merge_field(self.template, data.template, data.request_data)
        for field, value in cpy.headers.items():
            cpy.headers[field] = _template_field(value, data.request_data)
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

    def get_config_merged_with_data(self, appid: str, data: SendData):
        config = self.get_config(appid)
        if config is None:
            return None
        merged_app_config = config.merge_config_with_send_data(data)
        if merged_app_config.template is not None:
            template_config = self.get_template_config(merged_app_config.template)
            merged_template_config = template_config.merge_config_with_send_data(data)
            merged_app_config = merged_app_config.merge_with_template_config(merged_template_config)
        return merged_app_config

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


def load_json_dict(filename: str) -> dict:
    with open(filename) as fp:
        return json.load(fp)


configuration = Configuration.load_from_dict(load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'applications.json')),
                                             load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'templates.json')))
