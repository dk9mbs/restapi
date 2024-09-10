import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin

from services.orm import *
from shared.model import *

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        activity=api_activity()
        activity.msg_text.value=""
        activity.subject.value="insert"
        activity.type_id.value=4
        id=activity.insert(self.context)


        activity=api_activity.objects(self.context).select().where(api_activity.id==id).to_entity()
        activity.msg_text.value="test"
        activity.subject.value="test"
        activity.type_id.value=1
        activity.update(self.context)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
