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
        <restapi type="select">
            <table name="dummy" alias="d"/>
            <filter>
                <condition field="id" alias="d" value="99"/>
            </filter>

            <fields>
                <field name="name" value="test"/>
            </fields>

            <joins>
                <join table="api_user" alias="u" type="inner" condition="d.id=u.id"/>
            </joins>

            <select>
                <field name="username" table_alias="u"/>
                <field name="id" table_alias="d"/>
            </select>
        </restapi>
        """
        parser=FetchXmlParser(xml, self.context)
        parser.parse()

        print("=======================================")
        print("Test table_by_alias method:")
        print(f"Table by alias d: {parser.get_table_by_alias('d')}")
        print(f"Table by alias u: {parser.get_table_by_alias('u')}")
        print("=======================================")
        print("Test the not exists exception:")
        from core.exceptions import TableAliasNotFoundInFetchXml
        try:
            print(f"Table by not exists alias: {parser.get_table_by_alias('xxx')}")
        except TableAliasNotFoundInFetchXml as err:
            print(err)
        print("=======================================")

        print(f"SQL: {parser.get_sql()}")
        print("")
        print(f"Columns: {parser.get_columns()}")

        print ("********************")

        xml=f"""
        <restapi type="select">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>

            <select>
                <field name="id"/>
            </select>
        </restapi>
        """
        parser=FetchXmlParser(xml, self.context)
        parser.parse()

        print(parser.get_sql())

        print("\n\n\nGet all Fields with *:")
        print("------------------------------")
        xml=f"""
        <restapi type="select">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>
        </restapi>
        """
        parser=FetchXmlParser(xml, self.context)
        print(f"Columns: {parser.get_columns()}")

        print("==========================")


        print("\n\n\nUpdate Field:")
        xml=f"""
        <restapi type="update">
            <table name="dummy"/>
            <filter>
                <condition field="id" value="99"/>
            </filter>

            <fields>
                <field name="id">
                    <value><![CDATA[test12345<hallo>]]></value>
                </field>
            </fields>
        </restapi>
        """
        parser=FetchXmlParser(xml, self.context)
        parser.parse()

        print(parser.get_sql())

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
