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

    def test_by_table_alias(self):
        table_info=TableInfo(self.context, table_alias="log_data_exchange_fields")
        self.assertEqual(table_info.table_name, "meta_data_exchange_fields")
        self.assertEqual(table_info.table_alias, "log_data_exchange_fields")
        self.assertEqual(table_info.table_id, 20001)

    def test_by_table_name(self):
        table_info=TableInfo(self.context, table_name="meta_data_exchange_fields")
        self.assertEqual(table_info.table_name, "meta_data_exchange_fields")
        self.assertEqual(table_info.table_alias, "log_data_exchange_fields")
        self.assertEqual(table_info.table_id, 20001)

    def test_by_table_id(self):
        table_info=TableInfo(self.context, table_id=20001)
        self.assertEqual(table_info.table_name, "meta_data_exchange_fields")
        self.assertEqual(table_info.table_alias, "log_data_exchange_fields")
        self.assertEqual(table_info.table_id, 20001)

        print(table_info.fields)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
