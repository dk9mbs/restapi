import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.meta import build_table_fields_meta

class TestBuildMeta(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_add_all_new(self):
        #
        # Add new
        #
        print("inserting ...")
        #cursor=self.context.get_connection().cursor()
        #cursor.execute("TRUNCATE api_table_field;")
        #cursor.close()
        build_table_fields_meta(self.context)
        print("insert ok")

    def test_update_all(self):
        #
        # Update all fields
        #
        print("updating ...")
        build_table_fields_meta(self.context)
        print("update ok")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
