import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core.sql import exec_raw_sql

class TestFetchxmlParser(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_exec(self):
        sql="""
        DELETE FROM dummy WHERE id=%s;
        """
        exec_raw_sql(self.context, sql,[99])

        sql="""
        INSERT INTO dummy (id,name,port) VALUES (%s,%s,%s);
        """
        exec_raw_sql(self.context, sql,[99, 'test_database_concat', 1234])

        xml=f"""
        <restapi type="update">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
            <fields>
                <field name="name" value="TEST"/>
            </fields>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        DatabaseServices.exec(fetch,self.context)

        xml=f"""
        <restapi type="select">
            <table name="dummy" alias="d"/>
            <select>
                <field name="name" func="concat" string2="hallo" table_alias="d" 
                    if_condition_field="id" if_condition_value="99" string_before="before-" string_after="-after"
                    grouping="y" alias="name_with_pre_and_post" />
            </select>
            <filter type="or">
                <condition field="id" value="99" alias="d"/>
            </filter>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        rs=DatabaseServices.exec(fetch,self.context, fetch_mode=1)
        #self.assertIsNone(dummy.get_result())
        print(rs.get_result())
        self.assertEqual(rs.get_result()['name_with_pre_and_post'], "before-TEST-after")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
