import os
import copy
import json
from typing import List, Set, Dict, Union

from fsfe_forms.common.config import CONFIGURATION_FOLDER, CONFIRMATION_EMAIL_SUBJECT, CONFIRMATION_DUPLICATE_EMAIL_SUBJECT, DEFAULT_SUBJECT_LANG, LANG_STRING_TOKEN, TEMPLATES_FOLDER
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import TemplateRenderService


class TemplateContentConfig:
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content

    @classmethod
    def load_from_dict(cls, data: dict) -> 'TemplateContentConfig':
        filename = data.get('filename')
        if filename is not None:
            filename = os.path.join(TEMPLATES_FOLDER, filename)
        content = data.get('content')
        return cls(filename, content)

    def get_template(self, lang) -> str:
        if self.content:
            return self.content
        filename = self.get_filename(lang)
        with open(filename) as f:
            return f.read()

    def get_filename(self, lang, default_lang=DEFAULT_SUBJECT_LANG) -> str:
        if LANG_STRING_TOKEN in self.filename:
            filename = self.filename.format(lang=lang)
            if os.path.isfile(filename):
                return filename
            return self.filename.format(lang=default_lang)
        return self.filename


class TemplateConfig:
    def __init__(self, plain, html):
        self.html = html
        self.plain = plain

    @classmethod
    def load_from_dict(cls, data: Dict) -> 'TemplateConfig':
        html = TemplateContentConfig.load_from_dict(data['html']) if 'html' in data else None
        plain = TemplateContentConfig.load_from_dict(data['plain']) if 'plain' in data else None
        return cls(plain, html)

    def get_html_template(self, lang=None):
        return self.html.get_template(lang) if self.html is not None else None

    def get_plain_template(self, lang=None):
        return self.plain.get_template(lang) if self.plain is not None else None


class AppConfig:
    def __init__(self, send_from: str, send_to: List[str], reply_to: str, subject: str,
                 store: str,
                 confirm: bool, confirmation_check_duplicates: bool,
                 redirect: str, redirect_confirmed: str, template: TemplateConfig,
                 required_vars: Set[str], headers: dict,
                 confirmation_from: str, confirmation_template: TemplateConfig, confirmation_duplicate_template: TemplateConfig,
                 confirmation_subject: str, confirmation_duplicate_subject: str):
        self.confirmation_from = confirmation_from
        self.confirmation_template = confirmation_template
        self.confirmation_duplicate_template = confirmation_duplicate_template
        self.confirmation_subject = confirmation_subject
        self.confirmation_duplicate_subject = confirmation_duplicate_subject
        self.headers = headers
        self.template = template
        self.redirect = redirect
        self.redirect_confirmed = redirect_confirmed
        self.confirm = confirm
        self.confirmation_check_duplicates = confirmation_check_duplicates
        self.store = store
        self.subject = subject
        self.reply_to = reply_to
        self.send_to = send_to
        self.send_from = send_from
        self.required_vars = required_vars

    @classmethod
    def load_from_dict(cls, data: dict) -> 'AppConfig':
        template = TemplateConfig.load_from_dict(data['template']) if 'template' in data else None
        confirmation_template = TemplateConfig.load_from_dict(data['confirmation-template']) if 'confirmation-template' in data else None
        confirmation_duplicate_template = TemplateConfig.load_from_dict(data['confirmation-duplicate-template']) if 'confirmation-duplicate-template' in data else None
        args = {
            'template': template,
            'redirect': data.get('redirect'),
            'redirect_confirmed': data.get('redirect-confirmed'),
            'confirm': data.get('confirm'),
            'confirmation_check_duplicates': data.get('confirmation-check-duplicates', False),
            'store': data.get('store'),
            'subject': data.get('subject'),
            'reply_to': data.get('reply_to'),
            'send_to': list(data['to']) if 'to' in data else None,
            'send_from': data.get('from'),
            'required_vars': set(data.get('required_vars', [])),
            'headers': data.get('headers', {}),
            'confirmation_from': data.get('confirmation-from'),
            'confirmation_template': confirmation_template,
            'confirmation_duplicate_template': confirmation_duplicate_template,
            'confirmation_subject': data.get('confirmation-subject', CONFIRMATION_EMAIL_SUBJECT),
            'confirmation_duplicate_subject': data.get('confirmation-duplicate-subject', CONFIRMATION_DUPLICATE_EMAIL_SUBJECT)
        }
        return cls(**args)

    def merge_config_with_send_data(self, data: SendData) -> 'AppConfig':
        cpy = copy.deepcopy(self)
        request_data = data.request_data
        allowed_vars = ['send_from', 'send_to', 'reply_to', 'subject', 'template']
        # Iterate over each API parameter that can be erase by the request parameter
        for parameter_name in allowed_vars:
            # Take the parameter from user request if exist, else take from object
            parameter_value = getattr(data, parameter_name) or getattr(self, parameter_name)
            template = _render_template(parameter_value, request_data)
            # Set the value of the field to the template render
            setattr(cpy, parameter_name, template)
        cpy.confirmation_subject = _render_template(self.confirmation_subject, request_data)
        cpy.headers = _render_template(cpy.headers, request_data)
        return cpy


class Configuration:
    def __init__(self, appconfigs: Dict[str, AppConfig]):
        self.appconfigs = appconfigs

    def get_config(self, data: SendData) -> Union[None, AppConfig]:
        config = self.appconfigs.get(data.appid)
        if config is None:
            return None
        return config.merge_config_with_send_data(data)

    @classmethod
    def load_from_dict(cls, applications_configs: dict) -> 'Configuration':
        app_config = {appid: AppConfig.load_from_dict(conf) for appid, conf in applications_configs.items()}
        return cls(app_config)


def _render_template(parameter_value: Union[str, List, Dict], data: Dict) -> Union[str, List, Dict]:
    """
    Take a parameter and render it as a Jinja file or return the value
    If the parameter is a dict, we render it recursively
    """
    if isinstance(parameter_value, str):
        try:
            return TemplateRenderService.render_content(parameter_value, data)
        except:
            return parameter_value
    if isinstance(parameter_value, dict):
        return {k: _render_template(v, data) for k, v in parameter_value.items()}
    if isinstance(parameter_value, list):
        return [_render_template(p, data) for p in parameter_value]
    return parameter_value


def load_json_dict(filename: str) -> Dict:
    with open(filename) as fp:
        return json.load(fp)


configuration = Configuration.load_from_dict(load_json_dict(os.path.join(CONFIGURATION_FOLDER, 'applications.json')))
