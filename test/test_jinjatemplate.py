import unittest
import os

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from services.jinjatemplate import JinjaTemplate

class TestJinjaTemplate(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_execution(self):
        print("+++ Error page by error page +++")
        print(JinjaTemplate.render_status_template(500, "500 error page"))
        print("----------------------------")

        print("+++ Error page by default error page +++")
        print(JinjaTemplate.render_status_template(1234, "Default error page"))
        print("----------------------------")

        print("+++ Error page by String +++")
        print("For excample default.htm was deleted")
        # mock the config
        AppInfo.set_current_config("ui","wwwroot","/tmp")
        print(JinjaTemplate.render_status_template(500, "string error page"))
        print("----------------------------")

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
