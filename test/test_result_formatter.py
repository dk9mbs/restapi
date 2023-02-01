import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core.formatter_factory import FormatterFactory
from services.dataformatter import DataFormatter

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_formatter(self):
        from services.jinjatemplate import JinjaTemplate
        from core.fetchxmlparser import FetchXmlParser
        from services.database import DatabaseServices
        from core.meta import read_table_meta

        fetch=f"""
        <restapi type="select">
            <table name="api_session"/>
            <select>
                <field name="id"/>
                <field name="user_id"/>
                <field name="session_values"/>
                <field name="created_on"/>
                <field name="last_access_on"/>
                <field name="disabled"/>
            </select>
            <filter type="and">
                <condition field="disabled" value="0" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self.context)
        rs=DatabaseServices.exec(fetchparser, self.context,run_as_system=True, fetch_mode=0)

        formatter=DataFormatter(self.context,"test","api_session", rs.get_result())
        result = formatter.render()

        print(f"Result: {result}")

        #self.assertEqual(formatter.output(self.context, 0),"No")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
