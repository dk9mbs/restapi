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

    def test_add_user_group(self):
        
        from core.user_group_tools import UserGroupTools
        UserGroupTools.delete_private_user_group(self.context, 1)
        group=UserGroupTools.add_or_get_private_user_group(self.context, 1)
        UserGroupTools.add_record_permission(self.context, 20, 1, -999)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
