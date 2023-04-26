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
        from services.orm import Field, StringField, NumericField, BoolField, IntField, DateTimeField

        f=StringField("id","stringvalue")
        self.assertEqual(f.value , "stringvalue")

        f=NumericField("id",12.34)
        self.assertEqual(f.value , 12.34)

        f=NumericField("id","12.34")
        self.assertEqual(f.value , 12.34)

        f=NumericField("id","12.343453")
        f.format='{:.2f}'
        self.assertEqual(f.value , 12.343453)
        self.assertEqual(f.formatted_value , 12.34)

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

        """
        IntField
        """
        f=IntField("id", 99)
        self.assertEqual(f.value, 99)
        self.assertEqual(f.formatted_value, 99)

        f=IntField("id", -99)
        self.assertEqual(f.value, -99)
        self.assertEqual(f.formatted_value, -99)

        f=IntField("id", 99.18)
        self.assertEqual(f.value, 99)
        self.assertEqual(f.formatted_value, 99)

        f=IntField("id", "99.98")
        self.assertEqual(f.value, 99)
        self.assertEqual(f.formatted_value, 99)

        """
        Datetime
        """
        f=DateTimeField("created_on","2023-12-31 00:00:00", format="%d.%m.%Y %H:%M:%S")
        #f.format="%d.%m.%Y %H:%M:%S"
        print(f"Ausgabe (formatiert).......:{f.formatted_value}")
        print(f"Value (unformatiert).......:{f.value}")

        """
        Complex field tests
        """
        f=NumericField("id","12.348453")
        f.format='{:.2f}'
        self.assertEqual(f.value , 12.348453)
        self.assertEqual(f.formatted_value , 12.35)
        self.assertEqual(f.changed, False)
        f.value=11.5
        self.assertEqual(f.changed, True)
        self.assertEqual(f.formatted_value, 11.50)
        self.assertEqual(f.value, 11.5)



        f=BoolField("id")
        f.value=True
        self.assertEqual(f.value , True)

        #f.value="T"
        #self.assertEqual(f.value , True)

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
        from model.ApiGroup import ApiGroup

        item=Dummy.get_objects(context) \
            .select() \
            .where( [Q(id__eq=99) | Q(id__eq=100) | Q(id__eq=3) | Q(id__eq=4) , Q(name='test').alias("main")] ) \
            .orderby(O('id','DESC')) \
            .orderby(O('name', 'ASC')) \
            .to_list()

        #item=ApiGroup.get_objects(context) \
        #    .select() \
        #    .where([Q(id__eq=1).alias("main") & Q(id__eq=1).alias("main"), Q(groupname='sysadmin').alias("main")], logical_connector='OR' ) \
        #    .orderby(O('main.id','DESC')) \
        #    .orderby(O('main.groupname', 'ASC')) \
        #    .to_entity()

        #print(item.is_admin)
        #print(item.groupname)

    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()