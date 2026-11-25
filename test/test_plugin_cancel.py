import os
import sys
import tempfile
import unittest

from config import CONFIG
from core.appinfo import AppInfo
from core.fetchxmlparser import FetchXmlParser
from core.sql import exec_raw_sql
from services.database import DatabaseServices

#
# plugin_context['cancel'] in sync before plugins (core/plugin.py, services/database.py)
#
PLUGIN_CODE="""
calls=[]

def execute(context, plugin_context, params):
    calls.append(plugin_context['type'])
    data=params.get('data', None)
    if isinstance(data, dict) and 'name' in data and data['name']['value'] in ('__cancel__', '__cancel_async__'):
        plugin_context['cancel']=True
    if isinstance(data, dict) and 'name' in data and data['name']['value']=='__cancel_raise__':
        plugin_context['cancel']=True
        raise Exception('cancel test')
    if plugin_context['type']=='before' and not data:
        plugin_context['cancel']=True
"""

MODULE="test_plugin_cancel_module"
HANDLER_IDS=[900101,900102,900103,900104,900105,900106]

class TestPluginCancel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir=tempfile.TemporaryDirectory()
        with open(os.path.join(cls._dir.name, f"{MODULE}.py"), "w") as f:
            f.write(PLUGIN_CODE)
        sys.path.insert(0, cls._dir.name)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls._dir.name)
        cls._dir.cleanup()

    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

        self._remove_handlers()
        sql="""INSERT INTO api_event_handler (id,plugin_module_name,publisher,event,type,sorting,run_async)
            VALUES (%s,%s,'dummy',%s,%s,10,0)"""
        handlers=[('insert','before'),('insert','after'),('update','before'),
                  ('delete','before'),('select','before'),('select','after')]
        for id,(event,type) in zip(HANDLER_IDS, handlers):
            exec_raw_sql(self.context, sql, [id, MODULE, event, type], 0, False)
        self.context.commit()

        import test_plugin_cancel_module
        self.module=test_plugin_cancel_module
        self.module.calls.clear()

        self._remove_rows()
        exec_raw_sql(self.context, "INSERT INTO dummy (id,name,Port) VALUES (900001,'cancel',1)", [], 0, False)
        self.context.commit()

    def tearDown(self):
        self._remove_rows()
        self._remove_handlers()
        self.context.commit()
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

    def _remove_handlers(self):
        ids=",".join(str(x) for x in HANDLER_IDS)
        exec_raw_sql(self.context, f"DELETE FROM api_process_log WHERE event_handler_id IN ({ids})", [], 0, False)
        exec_raw_sql(self.context, f"DELETE FROM api_event_handler WHERE id IN ({ids})", [], 0, False)

    def _remove_rows(self):
        exec_raw_sql(self.context, "DELETE FROM dummy WHERE id BETWEEN 900001 AND 900009 OR name LIKE '\\_\\_cancel%%'", [], 0, False)

    def _exec(self, xml, fetch_mode=-1):
        return DatabaseServices.exec(FetchXmlParser(xml, self.context), self.context, fetch_mode=fetch_mode)

    def _count(self, name):
        rs=self._exec(f"""<restapi type="select"><table name="dummy"/>
            <filter><condition field="name" value="{name}"/></filter></restapi>""", fetch_mode=0)
        return len(rs.get_result())

    def test_insert_cancelled(self):
        rs=self._exec(f"""<restapi type="insert"><table name="dummy"/><fields>
            <field name="name" value="__cancel__"/><field name="Port" value="1"/>
            </fields></restapi>""", fetch_mode=0)
        self.assertEqual(rs.get_cursor().rowcount, 0)
        self.assertIsNone(rs.get_inserted_id())
        self.assertEqual(rs.get_result(), [])
        self.assertEqual(self.module.calls, ['before'])
        self.assertEqual(self._count("__cancel__"), 0)

    def test_insert_not_cancelled(self):
        rs=self._exec(f"""<restapi type="insert"><table name="dummy"/><fields>
            <field name="id" value="900002"/><field name="name" value="keep"/><field name="Port" value="1"/>
            </fields></restapi>""")
        self.assertEqual(rs.get_cursor().rowcount, 1)
        self.assertEqual(self.module.calls, ['before','after'])

    def test_exception_does_not_cancel(self):
        rs=self._exec(f"""<restapi type="insert"><table name="dummy"/><fields>
            <field name="id" value="900003"/><field name="name" value="__cancel_raise__"/><field name="Port" value="1"/>
            </fields></restapi>""")
        self.assertEqual(rs.get_cursor().rowcount, 1)

    def test_update_cancelled(self):
        rs=self._exec(f"""<restapi type="update"><table name="dummy"/>
            <fields><field name="name" value="__cancel__"/></fields>
            <filter><condition field="id" value="900001"/></filter></restapi>""")
        self.assertEqual(rs.get_cursor().rowcount, 0)
        self.assertEqual(self._count("cancel"), 1)

    def test_delete_cancelled(self):
        # delete has no fields in params['data'], the module cancels on an empty before
        rs=self._exec(f"""<restapi type="delete"><table name="dummy"/>
            <filter><condition field="id" value="900001"/></filter></restapi>""")
        self.assertEqual(rs.get_cursor().rowcount, 0)
        self.assertEqual(self._count("cancel"), 1)

    def test_select_not_cancelled(self):
        self.assertEqual(self._count("cancel"), 1)

    def test_async_cannot_cancel(self):
        exec_raw_sql(self.context, "UPDATE api_event_handler SET run_async=-1 WHERE id=%s", [HANDLER_IDS[0]], 0, False)
        self.context.commit()

        rs=self._exec(f"""<restapi type="insert"><table name="dummy"/><fields>
            <field name="id" value="900004"/><field name="name" value="__cancel_async__"/><field name="Port" value="1"/>
            </fields></restapi>""")
        self.assertEqual(rs.get_cursor().rowcount, 1)

if __name__ == '__main__':
    unittest.main()
