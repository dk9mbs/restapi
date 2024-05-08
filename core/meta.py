from core.exceptions import DataViewNotFound, TableMetaDataNotFound
from core.database import Recordset

def build_table_fields_meta(context):
    connection=context.get_connection()
    sql=f"UPDATE api_table SET name=alias WHERE name IS NULL OR name='';"
    cur_tables=connection.cursor()
    cur_tables.execute(sql)

    sql=f"""
    SELECT id, table_name FROM api_table ORDER BY id;
    """
    cur_tables=connection.cursor()
    cur_tables.execute(sql)
    rs_tables=Recordset(cur_tables)
    rs_tables.read()

    for table in rs_tables.get_result():
        table_name=table['table_name']
        table_id=table['id']

        sql=f"""
        SHOW FIELDS FROM {table_name};
        """
        cur_fields=connection.cursor()
        cur_fields.execute(sql)

        rs_fields=Recordset(cur_fields)
        rs_fields.read()
        for field in rs_fields.get_result():
            field_name=field['Field']
            referenced_table_id=None
            referenced_table_name=None
            referenced_field_name=None
            size=0
            is_lookup=False
            allow_null=__convert_boolean(field['Null'])
            default=field['Default']
            is_primary_key=__convert_boolean("0")

            filter=(table_name, field_name)
            sql="""
            SELECT k.TABLE_NAME,k.column_name
            FROM information_schema.table_constraints t
            JOIN information_schema.key_column_usage k
            USING(constraint_name,table_schema,table_name)
            WHERE t.constraint_type='PRIMARY KEY'
            AND t.table_schema=Database()
            AND t.table_name=%s
            AND k.COLUMN_NAME=%s;
            """
            cur_pk=connection.cursor()
            cursor=cur_pk.execute(sql, filter)
            rs_pk=Recordset(cur_pk)
            rs_pk.read()
            if not rs_pk.get_eof():
                is_primary_key=__convert_boolean("-1")
            rs_pk.close()

            filter=(table_name, field_name)
            sql="""
            SELECT TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=Database() AND TABLE_NAME=%s
            AND REFERENCED_TABLE_NAME IS NOT NULL AND COLUMN_NAME=%s;
            """
            cur_foreign=connection.cursor()
            cursor=cur_foreign.execute(sql, filter)
            rs_foreign=Recordset(cur_foreign)
            rs_foreign.read()
            if not rs_foreign.get_eof():
                referenced_table_name=rs_foreign.get_result()[0]['REFERENCED_TABLE_NAME']
                referenced_field_name=rs_foreign.get_result()[0]['REFERENCED_COLUMN_NAME']
                is_lookup=-1


                sql=f"""
                SELECT id FROM api_table WHERE table_name=%s
                """
                cur_tab=connection.cursor()
                cur_tab.execute(sql,[referenced_table_name])
                rs_tab=Recordset(cur_tab)
                rs_tab.read(fetch_mode=1)
                if not rs_tab.get_eof():
                    referenced_table_id=rs_tab.get_result()['id']
                rs_tab.close()

            rs_foreign.close()

            type_id=__convert_field_type(field_name, field['Type'], referenced_table_id)


            sql=f"""
            SELECT id FROM api_table_field WHERE table_id=%s AND name=%s
            """
            filter=(table_id, field_name)
            cur_meta=connection.cursor()
            cur_meta.execute(sql,filter)
            rs_meta=Recordset(cur_meta)
            rs_meta.read()
            if rs_meta.get_eof():

                sql="""
                INSERT INTO api_table_field(table_id, label, name, type_id, size, referenced_table_name,
                referenced_field_name, is_lookup, allow_null, default_value, referenced_table_id, is_primary_key)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """

                filter=(table_id, field_name, field_name, type_id, size, referenced_table_name, referenced_field_name, is_lookup,
                        allow_null, default, referenced_table_id, is_primary_key)
            else:

                if is_lookup==-1:
                    sql=f"""
                    UPDATE api_table_field SET type_id=%s,size=%s,referenced_table_name=%s,
                    referenced_field_name=%s,is_lookup=%s,allow_null=%s,default_value=%s,referenced_table_id=%s, is_primary_key=%s
                    WHERE table_id=%s AND name=%s;
                    """
                    filter=(type_id, size, referenced_table_name, referenced_field_name, is_lookup, allow_null, default,
                        referenced_table_id,is_primary_key, int(table_id), field_name )
                else:
                    sql=f"""
                    UPDATE api_table_field SET type_id=%s,size=%s,
                    allow_null=%s,default_value=%s, is_primary_key=%s
                    WHERE table_id=%s AND name=%s;
                    """
                    filter=(type_id, size, allow_null, default, is_primary_key,
                        int(table_id), field_name )

            #print(f"{sql} {filter}")
            cur_write=connection.cursor()
            cur_write.execute(sql, filter)
            cur_write.close()

        rs_fields.close()

    rs_tables.close()
    return True


def read_table_view_meta(context, table_id, view_name, type):
    connection=context.get_connection()
    filter=[table_id,view_name,type]

    sql=f"""
    SELECT * FROM api_table_view WHERE table_id=%s AND name=%s AND type_id=%s
    """

    cursor=connection.cursor()
    cursor.execute(sql,filter)
    meta=cursor.fetchone()
    cursor.fetchall()

    if meta==None:
        raise DataViewNotFound(f"View {view_name} with viewtype {type} notfound for table_id {table_id}")

    if meta['columns']=="" or meta['columns']==None:
        meta['columns']=None

    return meta

"""
Read the field metadata from a complete table
"""
def read_table_field_meta(context, table_alias=None, table_id=None):
    connection=context.get_connection()
    cursor=connection.cursor()
    meta_table=read_table_meta(context, alias="api_table")
    meta_field=read_table_meta(context, alias="api_table_field")
    meta_field_type=read_table_meta(context, alias="api_table_field_type")
    meta_field_control=read_table_meta(context, alias="api_table_field_control")

    where=""
    params=list()

    if table_alias!=None:
        where="t.alias=%s"
        params.append(table_alias)
    elif table_id!=None:
        where="t.id=%s"
        params.append(table_id)
    else:
        raise Exception('You must give table_id or table_alias')

    sql=f"""SELECT f.table_id,f.label,f.name,f.is_lookup,f.type_id,f.is_primary_key,
                f.size,f.allow_null,f.default_value,f.referenced_table_name,
                f.referenced_table_id,f.referenced_field_name,
                t.alias AS table_alias,
                control.control AS control,
                control.control_config AS control_config,
                f.control_config AS overwrite_control_config,field_name,f.is_virtual,rt.desc_field_name AS referenced_table_desc_field_name,
                rt.alias AS referenced_table_alias, type.orm_classname,
                CASE WHEN f.control_id IS NULL THEN type.control_id ELSE f.control_id END AS control_id
            FROM {meta_field['table_name']} f
            INNER JOIN {meta_table['table_name']} t ON t.id=f.table_id
            INNER JOIN {meta_field_type['table_name']} type ON type.id=f.type_id
            INNER JOIN {meta_field_control['table_name']} control ON control.id=CASE WHEN f.control_id IS NULL THEN type.control_id ELSE f.control_id END
            LEFT JOIN api_table rt ON rt.id=referenced_table_id
        WHERE { where }
        ORDER BY f.pos, f.id """
    cursor.execute(sql,params)
    meta=cursor.fetchall()

    from core.jsontools import merge
    import json
    for field in meta:
        json1=json.loads(field['control_config'])
        json2=json.loads(field['overwrite_control_config'])
        cfg=merge(json1, json2)
        field['control_config']=json.dumps(cfg)

    return meta


"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def read_table_meta(context, alias=None, table_name=None, table_id=None):
    connection=context.get_connection()
    filter=""
    if alias != None:
        sql=f"""
        SELECT * FROM api_table WHERE alias=%s
        """
        filter=alias
    elif table_name != None:
        sql=f"""
        SELECT * FROM api_table WHERE table_name=%s
        """
        filter=table_name
    elif table_id != None:
        sql=f"""
        SELECT * FROM api_table WHERE id=%s
        """
        filter=table_id
    else:
        raise NameError("table and alias are None!")

    cursor=connection.cursor()
    cursor.execute(sql,[filter])
    meta=cursor.fetchone()
    cursor.fetchall()
    if meta==None:
        raise TableMetaDataNotFound(f"Metadata not found for table_id:{table_id}, table_name:{table_name}, alias:{alias}")

    return meta




def __convert_boolean(value):
    if value=="YES": return -1
    if value=="-1": return -1
    if value=="1": return -1
    if value=="0": return 0
    if value=="NO": return 0

def __convert_field_type(field_name, value, referenced_table_id=None):
    if field_name.startswith("is_") and value.startswith("smallint") : return "boolean"
    if field_name.startswith("enable_") and value.startswith("smallint") : return "boolean"
    if not referenced_table_id==None:
        return "lookup"

    if value.startswith("varchar"): return "string"
    if value.startswith("int"): return "int"
    if value.startswith("smallint"): return "int"
    if value.startswith("decimal"): return "decimal"
    if value.startswith("datetime"): return "datetime"
    if value.startswith("date"): return "date"
    if value.startswith("timestamp"): return "timestamp"
    if value.startswith("time"): return "time"
    if value.startswith("text"): return "multiline"

    return "default"


