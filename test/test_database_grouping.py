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
            <table name="dummy" alias="d"/>
            <select>
                <field name="id" func="count"/>
                <field name="name" grouping="y"/>
            </select>
            <filter>
                <condition field="id" value="99" operator="geq" alias="d"/>
            </filter>
        </restapi>
        """
        print(xml)
        fetch=FetchXmlParser(xml, self.context)
        dummy=DatabaseServices.exec(fetch,self.context, fetch_mode=1)
        #self.assertIsNone(dummy.get_result())
        #print(dummy)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
