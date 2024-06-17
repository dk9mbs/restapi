import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.setting import Setting
from core.sql import exec_raw_sql

class TestFetchxmlParser(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_000_delete_all(self):
        sql="""
        DELETE FROM dummy;
        """
        exec_raw_sql(self.context, sql)

        sql=f"""
        DELETE FROM api_group_rec_permission WHERE record_id_int=%s;
        """
        exec_raw_sql(self.context, sql, [999])

    def test_001_insert(self):
        print("================ START INSERT =================")
        sql="""
        INSERT INTO dummy (name, port) VALUES (%s, %s);
        """
        params=['test core','1234']
        print(exec_raw_sql(self.context, sql, params))
        print("================ END INSERT =================")

    def test_002_update(self):
        print("================ START UPDATE =================")
        sql="""
        UPDATE dummy set name=%s WHERE port=%s;
        """
        params=['test update','1234']
        print(exec_raw_sql(self.context, sql, params))
        print("================ END UPDATE =================")

    def test_003_select(self):
        print("================ START SELECT =================")
        sql="""
        SELECT * FROM dummy;
        """
        params=['test123456']
        print(exec_raw_sql(self.context, sql, fetch_mode=1))
        print(exec_raw_sql(self.context, sql))
        print("================ END SELECT =================")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()