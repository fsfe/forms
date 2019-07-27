import json
import re


class Serializable:
    def toJSON(self):
        pass

    @classmethod
    def fromJSON(cls, data):
        pass


class SendData(Serializable):
    def __init__(self, appid, send_from, send_to, reply_to, subject, template, confirm, confirmed,
                 request_data, lang):
        self.request_data = request_data
        self.confirmed = confirmed
        self.appid = appid
        self.send_from = send_from
        self.send_to = send_to
        self.reply_to = reply_to
        self.subject = subject
        self.template = template
        self.confirm = confirm
        self.lang = get_secure_lang(lang)

    @classmethod
    def from_request(cls, appid: str, data: dict):
        send_from = data.get('from', None)
        send_to = data.get('to', None)
        if send_to is not None:
            send_to = send_to.split(',')
        reply_to = data.get('replyto', None)
        subject = data.get('subject', None)
        template = data.get('template', None)
        confirm = data.get('confirm', None)
        lang = data.get('lang', None)
        request_data = dict(data)
        return cls(appid, send_from, send_to, reply_to, subject, template, confirm, False, request_data, lang)

    def toJSON(self):
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, data):
        json_data = json.loads(data)
        appid = json_data.get('appid', None)
        send_from = json_data.get('send_from', None)
        send_to = json_data.get('send_to', None)
        reply_to = json_data.get('reply_to', None)
        subject = json_data.get('subject', None)
        template = json_data.get('template', None)
        confirm = json_data.get('confirm', None)
        delivered = json_data.get('delivered', False)
        request_data = json_data.get('request_data', None)
        lang = json_data.get('lang', None)
        return cls(appid, send_from, send_to, reply_to, subject, template, confirm, delivered, request_data, lang)

def get_secure_lang(lang):
    if lang and re.match('[a-z]{2}$', lang):
        return lang
    return None
