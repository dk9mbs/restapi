import unittest

from config import CONFIG
from core.appinfo import AppInfo
from core.fetchsqlparser import FetchSqlParser
from services.database import DatabaseServices
import api_mcp_schema

#
# Tests the MCP schema plugin for an admin (root) and a non-admin user.
# The non-admin user is 'mcp' (id 101) from install/db/basedata.sql:
# read-only on api_table and api_mcp_tool.
#
MCP_USER_ID=101

def _execute(context, input):
    params={"input": input, "output": {}}
    api_mcp_schema.execute(context, None, params)
    return params['output']

class TestPluginApiMcpSchema(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

        # the mcp user has a random password - read it as root
        parser=FetchSqlParser(f"SELECT password FROM api_user WHERE id={MCP_USER_ID}", self.context)
        rs=DatabaseServices.exec(parser, self.context, run_as_system=True, fetch_mode=1)
        self.assertIsNotNone(rs.get_result(), "user 'mcp' (id 101) missing - run install/db/basedata.sql")
        session_id=AppInfo.login("mcp", rs.get_result()['password'])
        self.mcp_context=AppInfo.create_context(session_id)

    def tearDown(self):
        AppInfo.save_context(self.mcp_context, True)
        AppInfo.logoff(self.mcp_context)
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

    def test_001_admin_sees_all_tables(self):
        tables=[t['table'] for t in _execute(self.context, {})['tables']]
        self.assertIn("api_mcp_tool", tables)
        self.assertIn("api_user", tables)
        self.assertGreater(len(tables), 2)

    def test_002_non_admin_sees_only_permitted_tables(self):
        tables=_execute(self.mcp_context, {})['tables']
        self.assertEqual(sorted([t['table'] for t in tables]), ["api_mcp_tool", "api_table"])
        for t in tables:
            self.assertFalse(t['can_create'])
            self.assertFalse(t['can_update'])
            self.assertFalse(t['can_delete'])

    def test_003_non_admin_describe_permitted_table(self):
        output=_execute(self.mcp_context, {"table": "api_mcp_tool"})
        self.assertEqual(output['table']['table'], "api_mcp_tool")
        fields=[f['name'] for f in output['fields']]
        self.assertIn("id", fields)
        self.assertIn("name", fields)

    def test_004_non_admin_describe_forbidden_table(self):
        with self.assertRaises(Exception):
            _execute(self.mcp_context, {"table": "api_user"})

    def test_005_describe_unknown_table(self):
        with self.assertRaises(Exception):
            _execute(self.context, {"table": "this_table_does_not_exist"})


if __name__ == '__main__':
    unittest.main()
