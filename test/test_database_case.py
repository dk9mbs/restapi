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
        <restapi type="select">
            <table name="iot_sensor_data" alias="d"/>
            <select>
                <field alias="created_on" name="created_on" func="date_format" format="%Y-%m-%d %H:00:00" grouping="y"/>
                <field func="avg" if_condition_field="sensor_id" if_condition_value="WOHNTEMP01" name="sensor_value" alias="WOHNTEMP01"/>
                <field func="avg" if_condition_field="sensor_id" if_condition_value="WOHNTEMP02" name="sensor_value" alias="WOHNTEMP02"/>
                <field func="avg" if_condition_field="sensor_id" if_condition_value="GARTTEMP01" name="sensor_value" alias="GARTTEMP01"/>
            </select>
        </restapi>
        """
        print(xml)
        fetch=FetchXmlParser(xml, self.context)
        dummy=DatabaseServices.exec(fetch,self.context, fetch_mode=1)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
