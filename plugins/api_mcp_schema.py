from core import log
from core.meta import read_all_table_meta, read_table_field_meta
from core.permission import Permission

logger=log.create_logger(__name__)

#
# Liefert dem MCP-Service das Datenmodell aus den restapi-Metadaten.
# Aufruf über /v1.0/action/api_mcp_schema
#
# params['input']={}                    -> alle Tabellen, die der angemeldete Benutzer lesen darf
# params['input']={"table":"<alias>"}   -> Felder dieser Tabelle
#
# Berechtigungen über core/permission.py (api_group_permission, Admins sehen alles).
#
def config():
    return {"raise_exception": True}

def _read_tables(context, username):
    permissions=Permission().read_table_permissions(context, username)

    tables=[]
    for t in read_all_table_meta(context):
        perm=permissions.get(t['id'])
        if perm==None or not perm['read']:
            continue
        table={
            "table": t['alias'],
            "label": t['name'],
            "id_field": t['id_field_name'],
            "description_field": t['desc_field_name'],
            "can_create": perm['create'],
            "can_update": perm['update'],
            "can_delete": perm['delete']
        }
        if t.get('description'):
            table['description']=t['description']
        tables.append(table)
    return tables

def _read_fields(context, table):
    fields=[]
    for f in read_table_field_meta(context, table_alias=table):
        if f['is_virtual']==-1:
            continue
        field={
            "name": f['name'],
            "label": f['label'],
            "type": f['type_id'],
            "is_primary_key": f['is_primary_key']==-1,
            "allow_null": f['allow_null']==-1,
            "is_read_only": f['is_read_only']==-1
        }
        if f['size']:
            field['size']=f['size']
        if f['referenced_table_alias']:
            field['references']=f['referenced_table_alias']
        fields.append(field)
    return fields

def execute(context, plugin_context, params):
    username=context.get_username()
    table=params['input'].get('table')

    tables=_read_tables(context, username)

    if table==None or table=="":
        params['output']['tables']=tables
        return

    # nur Tabellen beschreiben, die der Benutzer auch lesen darf
    match=[t for t in tables if t['table']==table]
    if len(match)==0:
        raise Exception(f"Tabelle '{table}' unbekannt oder keine Leseberechtigung")

    params['output']['table']=match[0]
    params['output']['fields']=_read_fields(context, table)
