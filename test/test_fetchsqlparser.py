import unittest

from config import CONFIG
from core.appinfo import AppInfo
from core.fetchsqlparser import FetchSqlParser
from services.database import DatabaseServices
from core.exceptions import (
    SqlStatementFormat,
    IdentifierNotAllowedInSqlStatement,
    OperatorNotAllowedInSqlStatement,
    FunctionNotAllowedInSqlStatement,
    LiteralNotAllowedInJoinCondition,
    TableMetaDataNotFound,
)

TEST_ID=777

class TestFetchSqlParser(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

    # ------------------------------------------------------------------
    # CRUD roundtrip against the real database, mirroring test_database_crud.py
    # but driven by SQL statements instead of fetchxml
    # ------------------------------------------------------------------

    def test_001_delete_all(self):
        sql=f"DELETE FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        DatabaseServices.exec(parser, self.context)

    def test_002_select_none(self):
        sql=f"SELECT * FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        rs=DatabaseServices.exec(parser, self.context, fetch_mode=1)
        self.assertIsNone(rs.get_result())

    def test_003_insert(self):
        sql=f"INSERT INTO dummy (id, name, port) VALUES ({TEST_ID}, 'FetchSqlParser Test', '3306')"
        parser=FetchSqlParser(sql, self.context)
        self.assertEqual(parser.get_sql_type(), "insert")
        DatabaseServices.exec(parser, self.context)

    def test_004_select_after_insert(self):
        sql=f"SELECT * FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        rs=DatabaseServices.exec(parser, self.context, fetch_mode=1)
        self.assertIsNotNone(rs.get_result())
        self.assertEqual(rs.get_result()['name'], "FetchSqlParser Test")

    def test_005_update(self):
        sql=f"UPDATE dummy SET name='FetchSqlParser Updated' WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        self.assertEqual(parser.get_sql_type(), "update")
        DatabaseServices.exec(parser, self.context)

    def test_006_select_after_update(self):
        sql=f"SELECT * FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        rs=DatabaseServices.exec(parser, self.context, fetch_mode=1)
        self.assertEqual(rs.get_result()['name'], "FetchSqlParser Updated")

    def test_007_delete_cleanup(self):
        sql=f"DELETE FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        DatabaseServices.exec(parser, self.context)

        sql=f"SELECT * FROM dummy WHERE id={TEST_ID}"
        parser=FetchSqlParser(sql, self.context)
        rs=DatabaseServices.exec(parser, self.context, fetch_mode=1)
        self.assertIsNone(rs.get_result())

    # ------------------------------------------------------------------
    # drop-in interface compatibility with FetchXmlParser
    # ------------------------------------------------------------------

    def test_020_interface_select(self):
        sql=f"""
        SELECT d.id, u.username AS uname
        FROM dummy d
        INNER JOIN api_user u ON d.id = u.id
        WHERE d.id = {TEST_ID}
        """
        parser=FetchSqlParser(sql, self.context)

        self.assertEqual(parser.get_sql_type(), "select")
        self.assertEqual(parser.get_main_table(), "dummy")
        self.assertEqual(parser.get_main_alias(), "dummy")
        self.assertIn("dummy", parser.get_tables())
        self.assertIn("api_user", parser.get_tables())
        self.assertEqual(parser.get_table_by_alias("d")['name'], "dummy")
        self.assertEqual(parser.get_table_by_alias("u")['name'], "api_user")
        self.assertEqual(parser.get_auto_commit(), False)
        self.assertEqual(parser.get_page_size(), 0)

        sql_text, params=parser.get_sql()
        self.assertIn("SELECT", sql_text)
        self.assertIn("%s", sql_text)
        self.assertEqual(params, [str(TEST_ID)])

    def test_021_interface_insert(self):
        sql=f"INSERT INTO dummy (id, name, port) VALUES ({TEST_ID}, 'x', '1')"
        parser=FetchSqlParser(sql, self.context)

        self.assertEqual(parser.get_sql_type(), "insert")
        self.assertIn("id", parser.get_sql_fields())
        self.assertEqual(parser.get_sql_fields()['name']['value'], "x")

    # ------------------------------------------------------------------
    # table-level / statement-level security checks
    # ------------------------------------------------------------------

    def test_030_reject_multi_statement(self):
        with self.assertRaises(SqlStatementFormat):
            FetchSqlParser("SELECT * FROM dummy; DROP TABLE dummy;", self.context)

    def test_031_reject_ddl(self):
        with self.assertRaises(SqlStatementFormat):
            FetchSqlParser("DROP TABLE dummy", self.context)

    def test_032_reject_delete_without_where(self):
        with self.assertRaises(SqlStatementFormat):
            FetchSqlParser("DELETE FROM dummy", self.context)

    def test_033_reject_update_without_where(self):
        with self.assertRaises(SqlStatementFormat):
            FetchSqlParser("UPDATE dummy SET name='x'", self.context)

    def test_034_reject_unknown_table(self):
        with self.assertRaises(TableMetaDataNotFound):
            FetchSqlParser("SELECT * FROM this_table_does_not_exist", self.context)

    def test_035_reject_schema_qualified_table(self):
        with self.assertRaises(IdentifierNotAllowedInSqlStatement):
            FetchSqlParser("SELECT * FROM other_schema.dummy", self.context)

    def test_036_reject_literal_in_join_condition(self):
        with self.assertRaises(LiteralNotAllowedInJoinCondition):
            FetchSqlParser(
                "SELECT * FROM dummy d JOIN api_user u ON d.id = 1",
                self.context,
            )

    def test_037_reject_disallowed_function(self):
        with self.assertRaises(FunctionNotAllowedInSqlStatement):
            FetchSqlParser("SELECT UPPER(name) FROM dummy", self.context)

    def test_038_reject_subquery_in_in_clause(self):
        with self.assertRaises(OperatorNotAllowedInSqlStatement):
            FetchSqlParser(
                "SELECT * FROM dummy d WHERE d.id IN (SELECT id FROM api_user)",
                self.context,
            )

    def test_039_reject_inline_limit(self):
        with self.assertRaises(SqlStatementFormat):
            FetchSqlParser("SELECT * FROM dummy LIMIT 10", self.context)


if __name__ == '__main__':
    unittest.main()
