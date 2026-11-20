import unittest
from unittest import mock

from config import CONFIG
from core.appinfo import AppInfo

"""
One database connection per request: login, create_context, save_context
and logoff share the connection instead of opening an own one each.
"""
class TestAppInfoConnection(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        self._create_connection=AppInfo.create_connection
        self.counter=mock.patch.object(AppInfo, 'create_connection', side_effect=self._create_connection)
        self.mock=self.counter.start()

    def tearDown(self):
        self.counter.stop()

    def _session_exists(self, session_id):
        connection=self._create_connection()
        cursor=connection.cursor()
        cursor.execute("SELECT id FROM api_session WHERE id=%s", [session_id])
        row=cursor.fetchone()
        connection.close()
        return row!=None

    def test_000_request_with_login(self):
        # like before_request: credentials, login and context on one connection
        connection=AppInfo.create_connection()
        guest=AppInfo.guest_credentials(connection=connection)
        session_id=AppInfo.login(guest['username'], guest['password'], connection=connection)
        self.assertNotEqual(session_id, None)
        self.assertTrue(connection.open)

        context=AppInfo.create_context(session_id, auto_logoff=True, connection=connection)
        self.assertIs(context.get_connection(), connection)
        self.assertEqual(context.get_username(), guest['username'])

        # like teardown_request with auto_logoff
        AppInfo.logoff(context)
        context.close()

        self.assertEqual(self.mock.call_count, 1)
        self.assertFalse(connection.open)
        self.assertFalse(self._session_exists(session_id))

    def test_001_request_with_session(self):
        session_id=self._login_root()
        self.mock.reset_mock()

        # like before_request with cookie/jwt and teardown_request without auto_logoff
        context=AppInfo.create_context(session_id)
        context.set_session_value('test_value', 'abc')
        AppInfo.save_context(context)
        self.assertEqual(self.mock.call_count, 1)
        self.assertFalse(context.get_connection().open)

        # session values are saved
        context=AppInfo.create_context(session_id)
        self.assertEqual(context.get_session_value('test_value'), 'abc')

        # logoff after save_context(close_context=True) opens an own connection
        AppInfo.save_context(context, True)
        AppInfo.logoff(context)
        self.assertFalse(self._session_exists(session_id))

    def test_002_save_context_without_close(self):
        session_id=self._login_root()
        context=AppInfo.create_context(session_id)
        AppInfo.save_context(context, close_context=False)
        self.assertTrue(context.get_connection().open)
        AppInfo.save_context(context, close_context=True)
        AppInfo.logoff(context)

    def test_003_wrong_password(self):
        connection=AppInfo.create_connection()
        session_id=AppInfo.login('root', 'wrong password', connection=connection)
        self.assertEqual(session_id, None)
        self.assertTrue(connection.open)
        connection.close()

        # without connection: own connection, closed again
        self.assertEqual(AppInfo.login('root', 'wrong password'), None)

    def test_004_unknown_session_closes_connection(self):
        connection=AppInfo.create_connection()
        with self.assertRaises(NameError):
            AppInfo.create_context('no-session', connection=connection)
        self.assertFalse(connection.open)

    def test_005_credentials_without_connection(self):
        self.assertEqual(AppInfo.guest_credentials()['username'], 'guest')
        self.assertEqual(AppInfo.system_credentials()['username'], 'system')

    def _login_root(self):
        session_id=AppInfo.login("root","password")
        self.assertNotEqual(session_id, None)
        return session_id

if __name__ == '__main__':
    unittest.main()
