import json
import unittest

from common.configurator import Configuration
from common.models import Serializable
from common.services import StorageService


class ConfiguratorTests(unittest.TestCase):
    def setUp(self):
        self.config = Configuration.load_from_dict({
            "1": {
                "ratelimit": 2,
                "from": "email1@example.com",
                "to": ["email1@example.com"],
                "subject": "Thank you!",
                "include_vars": True,
                "store": "data/emails.json",
                "redirect": "http://google.com"
            },
            "2": {
                "ratelimit": 10,
                "from": "email2@example.com",
                "to": ["email2@example.com"],
                "subject": "Thank you a lot!",
                "redirect": "http://facebook.com"
            }
        }, {
            "first_template": {
                "content": "<b>Hello, {{ name }}</b>"
            }
        })

    def test_config(self):
        self.assertEqual(2, len(self.config.appconfigs))
        self.assertEqual(1, len(self.config.tempconfigs))

        self.assertEqual("1", self.config.appconfigs[0].appid)
        appconf = self.config.appconfigs[0]
        self.assertEqual(2, appconf.ratelimit)
        self.assertEqual("email1@example.com", appconf.send_from)
        self.assertEqual(1, len(appconf.send_to))
        self.assertEqual("email1@example.com", appconf.send_to[0])
        self.assertEqual("Thank you!", appconf.subject)
        self.assertEqual(True, appconf.include_vars)
        self.assertEqual("data/emails.json", appconf.store)
        self.assertEqual("http://google.com", appconf.redirect)
        tempconf = self.config.tempconfigs[0]
        self.assertEqual("first_template", tempconf.name)
        self.assertEqual("<b>Hello, {{ name }}</b>", tempconf.content)
        self.assertEqual(None, tempconf.filename)


class TestData(Serializable):
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2

    def toJSON(self):
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, data):
        json_data = json.loads(data)
        field1 = json_data.get('field1', None)
        field2 = json_data.get('field2', None)
        return cls(field1, field2)


class StorageTests(unittest.TestCase):
    def test_store(self):
        table = 'testtable'
        data = TestData('qwerty', 12345)
        id = StorageService.create(table, data)
        resolved_data = StorageService.get(table, id, TestData)
        self.assertEqual(data.field1, resolved_data.field1)
        self.assertEqual(data.field2, resolved_data.field2)
