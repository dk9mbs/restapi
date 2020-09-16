import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser

class TestFetchxmlParser(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        #print("BEGIN of test_fetchxml")
        xml=f"""
        <restapi type="update">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
            <fields>
                <field name="name" value="test"/>
            </fields>
        </restapi>
        """
        parser=FetchXmlParser(xml, self.context)
        parser.parse()
        #print(parser.get_sql())
        #print("END of test_fetchxml")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
