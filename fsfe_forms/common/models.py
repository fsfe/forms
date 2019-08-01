import json
import re


class Serializable:
    def toJSON(self):
        pass

    @classmethod
    def fromJSON(cls, data):
        pass


class SendData(Serializable):
    def __init__(self, request_data):
        self.request_data = request_data

    @classmethod
    def from_request(cls, data: dict):
        return cls(data)

    def toJSON(self):
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, data):
        json_data = json.loads(data)
        request_data = json_data.get('request_data', None)
        if not 'appid' in request_data:  # old entries
            request_data['appid'] = json_data.get('appid')
        return cls(request_data)
