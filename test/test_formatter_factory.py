import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core.formatter_factory import FormatterFactory

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        factory=FormatterFactory(self.context, "boolean")
        formatter=factory.create()

        self.assertEqual(formatter.output(self.context, "fieldname",0),"No")
        self.assertEqual(formatter.output(self.context, "fieldname", None),"No")
        self.assertEqual(formatter.output(self.context, "fieldname", 1),"Yes")
        self.assertEqual(formatter.output(self.context, "fieldname", -1),"Yes")
        self.assertEqual(formatter.output(self.context, "fieldname", 999),"Yes")



    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
