import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        xml=f"""
        <restapi type="select">
            <table name="api_process_log" alias="l"/>
            <select>
                <field name="id" table_alias="l"/>
                <field name="request_msg" table_alias="l"/>
                <field name="publisher" table_alias="e"/>
                <field name="event" table_alias="e"/>
                <field name="type" table_alias="e"/>
            </select>
            <filter>
                <condition field="status_id" alias="l" value="20"/>
                <condition field="run_async" alias="l" value="-1"/>
                <condition field="last_retry_on" operator="olderThenXMinutes" alias="l" value="5"/>
            </filter>
            <joins>
                <join table="api_event_handler" alias="e" type="inner" condition="e.id=l.event_handler_id"/>
            </joins>
            <orderby>
                <field name="id" alias="l" sort="DESC"/>
            </orderby>
        </restapi>
        """

        fetch=FetchXmlParser(xml, self.context)
        rs=DatabaseServices.exec(fetch,self.context, fetch_mode=0)

        for item in rs.get_result():

            params={"data": item['request_msg']}
            type=item['type']
            plugin=Plugin(self.context, item['publisher'],item['event'], process_id=item['id'])

            plugin.execute(type, params)

            #self.assertEqual(params['name'], "GD77")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
