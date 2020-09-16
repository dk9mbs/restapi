import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from services.fetchxml import build_fetchxml_by_table_name, build_fetchxml_by_alias

class TestHetch(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_by_table(self):
        by_table=build_fetchxml_by_table_name(self.context,"dummy",id=100,data=None,auto_commit=0, type="select")

        print("====================")
        print(by_table)
        print("====================")

    def test_fetch_by_alias(self):
        by_alias=build_fetchxml_by_alias(self.context,"dummy",id=None,data={"port":"3306"},auto_commit=0, type="insert")

        print("====================")
        print(by_alias)
        print("====================")


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
