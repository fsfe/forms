import json
import re


class Serializable:
    def toJSON(self):
        pass

    @classmethod
    def fromJSON(cls, data):
        pass


class SendData(Serializable):
    def __init__(self, appid, confirm, request_data, lang):
        self.appid = appid
        self.confirm = confirm
        self.request_data = request_data
        self.lang = get_secure_lang(lang)

    @classmethod
    def from_request(cls, appid: str, data: dict):
        confirm = data.get('confirm', None)
        request_data = dict(data)
        lang = data.get('lang', None)
        return cls(appid, confirm, request_data, lang)

    def toJSON(self):
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, data):
        json_data = json.loads(data)
        appid = json_data.get('appid', None)
        confirm = json_data.get('confirm', None)
        request_data = json_data.get('request_data', None)
        lang = json_data.get('lang', None)
        return cls(appid, confirm, request_data, lang)

def get_secure_lang(lang):
    if lang and re.match('[a-z]{2}$', lang):
        return lang
    return None
