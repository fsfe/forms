import json
import re


class Serializable:
    def toJSON(self):
        pass

    @classmethod
    def fromJSON(cls, data):
        pass


class SendData(Serializable):
    def __init__(self, appid, confirm, request_data):
        self.appid = appid
        self.confirm = confirm
        self.request_data = request_data

    @classmethod
    def from_request(cls, data: dict):
        appid = data.get('appid')
        confirm = data.get('confirm')
        request_data = dict(data)
        return cls(appid, confirm, request_data)

    def toJSON(self):
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, data):
        json_data = json.loads(data)
        appid = json_data.get('appid', None)
        confirm = json_data.get('confirm', None)
        request_data = json_data.get('request_data', None)
        return cls(appid, confirm, request_data)
