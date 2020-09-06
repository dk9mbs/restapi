import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin

class TestPluginExecution(unittest.TestCase):
    def test_execution(self):

        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        context=AppInfo.create_context(session_id)


        params={"name":"IC735"}
        plugin=Plugin(context, 'dummy','update')
        print(f"\nBefore Execute: {params}")
        plugin.execute('before', params)
        plugin.execute('after', params)
        print(f"After execute {params}")
        self.assertEqual(params['name'], "GD77")

        AppInfo.save_context(context, True)
        AppInfo.logoff(context)


if __name__ == '__main__':
    unittest.main()
