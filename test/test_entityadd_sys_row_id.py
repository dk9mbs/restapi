import unittest
import uuid

from config import CONFIG
from core.appinfo import AppInfo
from core.fetchsqlparser import FetchSqlParser
from services.database import DatabaseServices

#
# Tests the idempotent insert of POST /v1.0/data/<table> (api/data/entityadd.py)
# with a client supplied __sys_row_id.
# api_provider is used, because it has no insert event handlers (dummy has).
#
TABLE="api_provider"
RECORD_ID="UNITTEST_SYSROWID"
RECORD_ID2="UNITTEST_SYSROWID2"
AUTH_HEADERS={"restapi-username": "root", "restapi-password": "password"}

class TestEntityAddSysRowId(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # restapi builds the flask app and registers all endpoints on import
        import restapi
        cls.client=restapi.app.test_client()

    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)
        self._delete()

    def tearDown(self):
        self._delete()
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

    def _delete(self):
        parser=FetchSqlParser(f"DELETE FROM {TABLE} WHERE id IN ('{RECORD_ID}','{RECORD_ID2}')", self.context)
        DatabaseServices.exec(parser, self.context, run_as_system=True)
        self.context.get_connection().commit()

    def _read_sys_row_id(self):
        parser=FetchSqlParser(f"SELECT sys_row_id FROM {TABLE} WHERE id='{RECORD_ID}'", self.context)
        rs=DatabaseServices.exec(parser, self.context, run_as_system=True, fetch_mode=1)
        if rs.get_result()==None:
            return None
        return rs.get_result()['sys_row_id']

    def _post(self, data):
        return self.client.post(f"/api/v1.0/data/{TABLE}", json=data, headers=AUTH_HEADERS)

    def test_001_insert_with_sys_row_id(self):
        row_id=str(uuid.uuid4())
        response=self._post({"id": RECORD_ID, "name": "unittest", "__sys_row_id": row_id})
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        self.assertEqual(response.get_json()['rows_affected'], 1)
        self.assertEqual(self._read_sys_row_id(), row_id)

    def test_002_sys_row_id_is_normalized(self):
        row_id=uuid.uuid4()
        response=self._post({"id": RECORD_ID, "name": "unittest", "__sys_row_id": str(row_id).upper()})
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        self.assertEqual(self._read_sys_row_id(), str(row_id))

    def test_003_duplicate_sys_row_id_returns_409(self):
        row_id=str(uuid.uuid4())
        response=self._post({"id": RECORD_ID, "name": "unittest", "__sys_row_id": row_id})
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))

        # other primary key, same sys_row_id: only the sys_row_id unique key is violated
        response=self._post({"id": RECORD_ID2, "name": "unittest", "__sys_row_id": row_id})
        self.assertEqual(response.status_code, 409, response.get_data(as_text=True))

    def test_004_invalid_sys_row_id_returns_400(self):
        response=self._post({"id": RECORD_ID, "name": "unittest", "__sys_row_id": "no-uuid"})
        self.assertEqual(response.status_code, 400, response.get_data(as_text=True))
        self.assertIsNone(self._read_sys_row_id())

    def test_005_plain_sys_row_id_is_ignored(self):
        row_id=str(uuid.uuid4())
        response=self._post({"id": RECORD_ID, "name": "unittest", "sys_row_id": row_id})
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        sys_row_id=self._read_sys_row_id()
        self.assertIsNotNone(sys_row_id)
        self.assertNotEqual(sys_row_id, row_id)


if __name__ == '__main__':
    unittest.main()
