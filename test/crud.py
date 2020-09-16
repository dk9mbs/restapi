import xml.etree.ElementTree as ET

from core.database import CommandBuilderFactory as factory, DbConnection, FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from services.fetchxml import read_dataview_meta

AppInfo.init(__name__, CONFIG['default'])
connection=DbConnection(AppInfo.create_connection())

fetch="""
<restapi>
    <table name="api_user"/>
    <select>
        <field name="id;select id from log_logs;--"/>
        <field name="username"/>
    </select>
</restapi>
"""

fetch="""
<restxml>
<table name="api_user" alias="u"/>
<select>
    <field name="mode_create" table_alias="p"/>
    <field name="mode_read" table_alias="p"/>
    <field name="mode_update" table_alias="p"/>
    <field name="mode_delete" table_alias="p"/>
    <field name="is_admin" table_alias="u" alias="user_is_admin"/>
    <field name="username" table_alias="u"/>
    <field name="table_id" table_alias="p"/>
</select>
<joins>
    <join type="inner" table="api_user_group" alias="ug" condition="ug.user_id=u.id"/>
    <join type="inner" table="api_group_permission" alias="p" condition="p.group_id=ug.group_id"/>
    <join type="inner" table="api_table" alias="t" condition="t.id=p.table_id"/>
</joins>
<filter type="and">
    <condition alias="t" field="table_name" operator="=" value="dummy"/>
    <condition alias="u" field="username" operator="=" value="guest"/>
    <condition alias="p" field="mode_read" operator="=" value="-1"/>
</filter>
</restxml>
"""


parser=FetchXmlParser(fetch)
parser.parse()
sql,params=parser.get_select()
print(sql)
print(parser._tables)

builder=factory.create_command('select', fetchxml=fetch);
cursor=connection.execute(builder)
print(cursor.fetchall())

#builder=factory.create_command('delete', fetch_xml=fetch);
#connection.execute(builder)

#builder=factory.create_command('insert', fetch_xml=fetch);
#connection.execute(builder)

#builder=factory.create_command('update', fetch_xml=fetch);
#connection.execute(builder)

connection.commit()
connection.close()


