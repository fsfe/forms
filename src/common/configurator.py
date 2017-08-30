import copy
import json
from typing import List
from common.models import SendData
from common.services import TemplateRenderService
import os

CONFIGURATION_FOLDER = "configuration"
TEMPLATES_FOLDER = "configuration/templates"


class AppConfig:
    def __init__(self, appid: str, ratelimit: int, send_from: str, send_to: List[str], reply_to: str, subject: str,
                 content: str, include_vars: bool, store: str, confirm: bool, redirect: str, template):
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

    @classmethod
    def load_from_dict(cls, appid: str, dict: dict):
        ratelimit = dict.get('ratelimit', None)
        template = dict.get('template', None)
        redirect = dict.get('redirect', None)
        confirm = dict.get('confirm', None)
        store = dict.get('store', None)
        include_vars = dict.get('include_vars', False)
        content = dict.get('content', None)
        subject = dict.get('subject', None)
        reply_to = dict.get('reply_to', None)
        send_to = dict.get('to', None)
        send_to = list(send_to) if send_to is not None else None
        send_from = dict.get('from', None)
        return cls(appid, ratelimit, send_from, send_to, reply_to, subject, content, include_vars, store, confirm,
                   redirect, template)

    def merge_config_with_send_data(self, data: SendData):
        cpy = copy.deepcopy(self)
        cpy.send_from = self._merge_field(self.send_from, data.send_from, data.request_data)
        cpy.send_to = self._merge_field(self.send_to, data.send_to, data.request_data)
        cpy.reply_to = self._merge_field(self.reply_to, data.reply_to, data.request_data)
        cpy.subject = self._merge_field(self.subject, data.subject, data.request_data)
        cpy.content = self._merge_field(self.content, data.content, data.request_data)
        cpy.template = self._merge_field(self.template, data.template, data.request_data)
        cpy.confirm = self._merge_field(self.confirm, data.confirm, data.request_data)
        return cpy

    @staticmethod
    def _merge_field(config_field, data_field, request_data: dict):
        selected_field = data_field if config_field is None else config_field
        if isinstance(selected_field, str):
            try:
                return TemplateRenderService.render_content(selected_field, request_data)
            except:
                return selected_field
        return selected_field


class TemplateConfig:
    def __init__(self, name: str, filename: str, content: str):
        self.name = name
        self.filename = filename
        self.content = content
        self._contents = None

    @classmethod
    def load_from_dict(cls, name: str, dict: dict):
        filename = dict.get('filename', None)
        if filename is not None:
            filename = os.path.join(TEMPLATES_FOLDER, filename)
        content = dict.get('content', None)
        return cls(name, filename, content)

    def get_template(self):
        if self._contents is None:
            if self.content is not None:
                self._contents = self.content
            elif self.filename is not None:
                with open(self.filename) as f:
                    self._contents = f.read()
        return self._contents


class Configuration:
    def __init__(self, appconfigs: List[AppConfig], tempconfigs: List[TemplateConfig]):
        self.appconfigs = appconfigs
        self.tempconfigs = tempconfigs

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
