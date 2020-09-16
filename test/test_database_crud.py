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
        <restapi type="delete">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
        </restapi>
        """
        fetch=FetchXmlParser(xml,self.context)
        DatabaseServices.exec(fetch,self.context)

        xml=f"""
        <restapi type="select">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        dummy=DatabaseServices.exec(fetch,self.context, fetch_mode=1)
        self.assertIsNone(dummy.get_result())

        xml=f"""
        <restapi type="insert">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
            <fields>
                <field name="id" value="99"/>
                <field name="name" value="IC735"/>
                <field name="port" value="3306"/>
            </fields>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        DatabaseServices.exec(fetch,self.context)

        xml=f"""
        <restapi type="select">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        dummy=DatabaseServices.exec(fetch,self.context, fetch_mode=1)
        self.assertIsNotNone (dummy.get_result())

        xml=f"""
        <restapi type="update">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
            <fields>
                <field name="name" value="UPDATE"/>
            </fields>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        DatabaseServices.exec(fetch,self.context)

        xml=f"""
        <restapi type="select">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
        </restapi>
        """
        fetch=FetchXmlParser(xml, self.context)
        dummy=DatabaseServices.exec(fetch,self.context, fetch_mode=1)
        self.assertEqual(dummy.get_result()['name'], "UPDATE")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)


if __name__ == '__main__':
    unittest.main()
