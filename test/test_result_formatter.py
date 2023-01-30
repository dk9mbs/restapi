import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core.formatter_factory import FormatterFactory
from services.dataformatter import DataFormatter

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_formatter(self):
        formatter=DataFormatter(self.context, {"id": "12", "name": "Markus"}, "Meine ID lautet: {{ id }} Hallo Welt")
        result = formatter.render()

        print(f"Result: {result}")

        #self.assertEqual(formatter.output(self.context, 0),"No")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
