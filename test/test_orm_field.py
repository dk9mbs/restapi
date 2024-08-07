import unittest

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.plugin import Plugin

from services.orm import Field, StringField, NumericField, BoolField, IntField, DateTimeField
from services.orm import WhereExpression, OrderByExpression

class TestPluginExecution(unittest.TestCase):
    def setUp(self):
        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        self.context=AppInfo.create_context(session_id)

    #def test_ormparser(self):
    #    from core.ormparser import OrmParser


        #parser = OrmParser(info, self.context)

    def test_field(self):

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
        #print(f"Ausgabe (formatiert).......:{f.formatted_value}")
        #print(f"Value (unformatiert).......:{f.value}")

        """
        Complex field tests
        """
        f=NumericField("id","12.348453")
        f.format='{:.2f}'
        self.assertEqual(f.value , 12.348453)
        self.assertEqual(f.formatted_value , 12.35)
        self.assertEqual(f.dirty, False)
        f.value=11.5
        self.assertEqual(f.dirty, True)
        self.assertEqual(f.formatted_value, 11.50)
        self.assertEqual(f.value, 11.5)



        f=BoolField("id")
        f.value=True
        self.assertEqual(f.value , True)

        try:
            f.value="True"
            self.fail("Das darf nicht sein!!!!")
        except ValueError as err:
            pass

    def test_000_orm(self):
        from config import CONFIG
        from core.appinfo import AppInfo
        from services.orm import BaseManager, BaseModel, F
        #from model.dummy import Dummy
        #from model.ApiGroup import ApiGroup
        from shared.model import api_group as ApiGroup
        from shared.model import dummy as Dummy

        AppInfo.init(__name__, CONFIG['default'])
        session_id=AppInfo.login("root","password")
        context=AppInfo.create_context(session_id)


        condition=ApiGroup.groupname == "test"
        self.assertEqual(condition.expression, 'api_group.groupname = %s')
        self.assertEqual(condition.values, ['test'])

        item=ApiGroup.objects(context) \
            .select() \
            .where(ApiGroup.groupname == "sysadmin") \
            .orderby(ApiGroup.groupname.desc()) \
            .orderby(ApiGroup.id.asc() ) \
            .to_entity()
        self.assertEqual(item.id, 1)
        self.assertEqual(item.groupname, "sysadmin")
        self.assertEqual(item.solution_id_url , "/api/v1.0/data/api_solution/1")
        self.assertEqual(item.solution_id_name , "restapi")
        self.assertEqual(ApiGroup.id.name, 'id')


        """
        Delete 999
        """
        Dummy.objects(context).delete().where(Dummy.id==999).execute()
        """
        Create a dummy with id=999
        """
        item=Dummy(id=999, Port=3307,name="test")
        item.insert(context)
        self.assertEqual(item.Port, 3307)
        self.assertEqual(item.name, "test")
        self.assertEqual(item.id, 999)
        """
        Read the created dummy
        """
        item=Dummy.objects(context).select().where(Dummy.id==999).to_entity()
        self.assertEqual(item.id, 999)
        self.assertEqual(item.Port, 3307)
        self.assertEqual(item.name, "test")
        """
        update the item
        """
        Dummy(id=999, Port=1234).update(context)

        item=Dummy.objects(context).select().where(Dummy.id==999).to_entity()
        self.assertEqual(item.Port, 1234)
        self.assertEqual(item.id, 999)

        """
        insert 998 into dummy table
        """
        Dummy.objects(context).delete().where(Dummy.id==998).execute()
        item2=Dummy(id=998, name="hallo", Port=0)
        item2.insert(context)


    def test_expression(self):
        expression=WhereExpression("name", "=", "Markus")
        self.assertEqual(expression.values, ['Markus'])

        expression=WhereExpression("name", "<", ['Markus'])
        self.assertEqual(expression.values, ['Markus'])

        expression=WhereExpression("name", ">", ['Markus'])
        self.assertEqual(expression.values, ['Markus'])

    def test_order_by(self):
        from shared.model import api_group as ApiGroup
        from shared.model import dummy as Dummy
        from services.orm import OrderByExpression

        o=Dummy.id.desc() & Dummy.Port.asc()
        self.assertEqual(o.expression, "dummy.id DESC,dummy.Port ASC")


    def test_001_two_entities(self):
        from shared.model import dummy
        item1=dummy.objects(self.context).select().where(dummy.id==999).to_entity()
        item2=dummy.objects(self.context).select().where(dummy.id==998).to_entity()

        self.assertEqual(item1.id.value, 999)
        self.assertEqual(item2.id.value, 998)



    def tearDown(self):
        AppInfo.save_context(self.context, True)
        AppInfo.logoff(self.context)

if __name__ == '__main__':
    unittest.main()
