import unittest
import xml.etree.ElementTree as ET

from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser, escape_xml_value
from core.exceptions import IdentifierNotAllowedInFetchXml, SpecialCharsInFetchXml

"""
Names, keywords and join conditions in fetchxml must be plain values.
"""
class TestFetchxmlValidation(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def tearDown(self):
        AppInfo.logoff(self.context)
        self.context.close()

    def _sql(self, xml):
        return FetchXmlParser(xml, self.context).get_sql()

    def _assert_rejected(self, xml, error=IdentifierNotAllowedInFetchXml):
        with self.assertRaises(error):
            self._sql(xml)

    def test_000_valid_fetchxml(self):
        sql, params=self._sql("""
        <restapi type="select">
            <table name="api_user" alias="u"/>
            <joins>
                <join table="api_user_group" alias="ug" type="LEFT" condition="ug.user_id=u.id AND ug.user_id = u.id"/>
            </joins>
            <select>
                <field name="username" table_alias="u" alias="name"/>
                <field name="id" table_alias="u" func="count" alias="cnt"/>
            </select>
            <filter type="or">
                <condition field="username" alias="u" value="root"/>
                <filter type="AND">
                    <condition field="id" alias="u" operator="geq" value="1"/>
                </filter>
            </filter>
            <orderby>
                <field name="username" alias="u" sort="desc"/>
            </orderby>
            <comment text="from test"/>
        </restapi>
        """)
        self.assertIn("left join api_user_group ug ON (ug.user_id=u.id AND ug.user_id = u.id)", sql)
        self.assertIn("ORDER BY u.username DESC", sql)
        self.assertIn("COUNT(u.id) cnt", sql)
        self.assertEqual(params, ['root', '1'])

    def test_001_orderby(self):
        self._assert_rejected('<restapi type="select"><table name="dummy"/><orderby><field name="id, name"/></orderby></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><orderby><field name="id" alias="d.x"/></orderby></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><orderby><field name="id" sort="ASC, id"/></orderby></restapi>')

    def test_002_condition(self):
        self._assert_rejected('<restapi type="select"><table name="dummy"/><filter><condition field="id=id OR 1" value="1"/></filter></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><filter><condition field="id" alias="x y" value="1"/></filter></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><filter type="AND 1=1"><condition field="id" value="1"/></filter></restapi>')

    def test_003_select(self):
        self._assert_rejected('<restapi type="select"><table name="dummy"/><select><field name="id" func="sleep"/></select></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><select><field name="id" alias="a b"/></select></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy"/><select><field name="id" table_alias="dummy d"/></select></restapi>')

    def test_004_join(self):
        base='<restapi type="select"><table name="api_user" alias="u"/><joins><join table="api_user_group" alias="ug" {}/></joins></restapi>'
        self._assert_rejected(base.format('condition="ug.user_id=u.id OR 1=1"'))
        self._assert_rejected(base.format('condition="(ug.user_id=u.id)"'))
        self._assert_rejected(base.format('type="cross" condition="ug.user_id=u.id"'))
        self._assert_rejected('<restapi type="select"><table name="api_user" alias="u"/><joins><join table="api_user_group" alias="ug x" condition="ug.user_id=u.id"/></joins></restapi>')

    def test_005_fields_table_and_comment(self):
        self._assert_rejected('<restapi type="insert"><table name="dummy"/><fields><field name="name=1, Port" value="1"/></fields></restapi>')
        self._assert_rejected('<restapi type="select"><table name="dummy" alias="d where 1"/></restapi>')
        self._assert_rejected('<restapi type="delete"><table name="dummy"/><filter><condition field="id" value="1"/></filter><comment text="*/ OR 1=1 /*"/></restapi>',
            SpecialCharsInFetchXml)

    def test_006_escape_xml_value(self):
        value='1" operator="neq'
        xml=f'<restapi type="delete"><table name="dummy"/><filter><condition field="id" value="{escape_xml_value(value)}"/></filter></restapi>'
        condition=ET.fromstring(xml).find("./filter/condition")
        self.assertEqual(condition.attrib['value'], value)
        self.assertNotIn('operator', condition.attrib)

        sql, params=self._sql(xml)
        self.assertIn("dummy.id=%s", sql)
        self.assertEqual(params, [value])

        self.assertEqual(escape_xml_value("<a & 'b'>"), "&lt;a &amp; &apos;b&apos;&gt;")
        self.assertEqual(escape_xml_value(42), "42")

    def test_007_record_permission_main_table(self):
        # api_file has enable_record_permission
        for xml in ("""
            <restapi type="select">
                <table name="api_file" alias="f"/>
                <joins><join table="api_user" alias="u" type="left" condition="u.id=f.id"/></joins>
            </restapi>""", """
            <restapi type="select">
                <joins><join table="api_user" alias="u" type="left" condition="u.id=f.id"/></joins>
                <table name="api_file" alias="f"/>
            </restapi>"""):
            parser=FetchXmlParser(xml, self.context)
            sql, params=parser.get_sql()
            self.assertIn("api_fn_rec_permission('root','api_file',f.id, 'READ')", sql)
            self.assertEqual(sql.count("api_fn_rec_permission"), 1)

            # get_sql() twice (count and select) adds the clause only once
            sql, params=parser.get_sql(True)
            self.assertEqual(sql.count("api_fn_rec_permission"), 1)

        # a field name does not switch off the record permission
        sql, params=self._sql("""
            <restapi type="select">
                <table name="api_file" alias="f"/>
                <filter><condition field="api_fn_rec_permission" operator="notnull"/></filter>
            </restapi>""")
        self.assertIn("api_fn_rec_permission('root'", sql)

if __name__ == '__main__':
    unittest.main()
