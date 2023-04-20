import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    def test_field(self):
        from services.orm import Field, StringField, NumericField, BoolField

        f=StringField("id","stringvalue")
        self.assertEqual(f.value , "stringvalue")

        f=NumericField("id",12.34)
        self.assertEqual(f.value , 12.34)

        f=BoolField("id",1)
        self.assertEqual(f.value , True)

        f=BoolField("id",-1)
        self.assertEqual(f.value , True)

        f=BoolField("id",0)
        self.assertEqual(f.value , False)

        f=BoolField("id",True)
        self.assertEqual(f.value , True)

        f=BoolField("id",False)
        self.assertEqual(f.value , False)

        f=BoolField("id",True)
        self.assertEqual(f.value , True)

        f=BoolField()
        f.name="id"
        f.value=True
        self.assertEqual(f.value , True)
    
        try:
            f.value="True"
            self.fail("Das darf nicht sein!!!!")
        except ValueError as err:
            pass

    def test_orm(self):
        from config import CONFIG
        from core.appinfo import AppInfo

        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        context=AppInfo.create_context(session_id)
        # dk9mbs

        from services.orm import BaseManager, BaseModel, Q, F, O
        from model.dummy import Dummy
        item=Dummy.get_objects(context) \
            .select() \
            .where( [Q(id__eq=99) | Q(id__eq=100) | Q(id__eq=3) | Q(id__eq=4) , Q(name='test')] ) \
            .orderby(O('id','DESC')) \
            .orderby(O('name', 'ASC')) \
            .to_entity()

        print(item)


    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
