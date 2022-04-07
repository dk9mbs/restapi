import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices

class TestFetchxmlParser(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_exec(self):
        xml=f"""
        <restapi type="select" limit="100" offset="0">
            <table name="iot_sensor_data" alias="u"/>
            <select>
                <field name="sensor_value" table_alias="u"/>
                <field name="sensor_id" table_alias="u"/>
            </select>
            <orderby>
                <field name="id" alias="u" sort="DESC"/>
            </orderby>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        rs=DatabaseServices.exec(fetch,self.context, fetch_mode=0)
        list=DatabaseServices.recordset_to_list(self.context, rs, {"sensor_value", "sensor_id"})
        self.assertIsNotNone(rs.get_result())

        print(list)


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
