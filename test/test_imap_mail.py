import unittest

from core.database import CommandBuilderFactory
from config import CONFIG
from core.appinfo import AppInfo
from plugins.api_imap_mail import execute as test_exec

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        context=self.context
        test_exec(context, {}, {})


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
