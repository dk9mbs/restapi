import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.meta import read_table_view_meta, read_table_meta

class TestMetaTableView(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_by_table(self):
        meta_table=read_table_meta(self.context, alias="dummy")
        meta=read_table_view_meta(self.context,meta_table['id'], "default")

        print("====================")
        print(meta)
        print("====================")

        #meta_table=read_table_meta(self.context, alias="notexists")
        #meta=read_table_view_meta(self.context,-999, "default")

        #print("====================")
        #print(meta)
        #print("====================")


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
