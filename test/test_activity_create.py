import unittest

#from core.database import CommandBuilderFactory
#from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from services.table_info import TableInfo

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_001_create_activity_by_tag(self):
        from services.activity import ActivityTools

        tools=ActivityTools()
        id=tools.create_alert_if_not_exists(self.context, "titel", "tag2", 1)

        print(id)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
