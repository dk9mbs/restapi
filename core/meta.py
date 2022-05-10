from core.exceptions import DataViewNotFound, TableMetaDataNotFound
from core.database import Recordset

def build_table_fields_meta(context):
    connection=context.get_connection()

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
                referenced_field_name, is_lookup, allow_null, default_value, referenced_table_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """

                filter=(table_id, field_name, field_name, type_id, size, referenced_table_name, referenced_field_name, is_lookup,
                        allow_null, default, referenced_table_id )
            else:
                sql=f"""
                UPDATE api_table_field SET type_id=%s,size=%s,referenced_table_name=%s,
                referenced_field_name=%s,is_lookup=%s,allow_null=%s,default_value=%s,referenced_table_id=%s
                WHERE table_id=%s AND name=%s;
                """
                filter=(type_id, size, referenced_table_name, referenced_field_name, is_lookup, allow_null, default,
                        referenced_table_id, int(table_id), field_name )

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

    return meta

"""
Read the field metadata from a complete table
"""
def read_table_field_meta(context, table_alias):
    connection=context.get_connection()
    cursor=connection.cursor()
    meta_table=read_table_meta(context, alias="api_table")
    meta_field=read_table_meta(context, alias="api_table_field")
    meta_field_type=read_table_meta(context, alias="api_table_field_type")
    meta_field_control=read_table_meta(context, alias="api_table_field_control")

    sql=f"""SELECT f.table_id,f.label,f.name,f.is_lookup,f.type_id,
                f.size,f.allow_null,f.default_value,f.referenced_table_name,
                f.referenced_table_id,f.referenced_field_name,
                t.alias AS table_alias,
                control.control AS control,
                control.control_config AS control_config,
                f.control_config AS overwrite_control_config,
                CASE WHEN f.control_id IS NULL THEN type.control_id ELSE f.control_id END AS control_id
            FROM {meta_field['table_name']} f
            INNER JOIN {meta_table['table_name']} t ON t.id=f.table_id
            INNER JOIN {meta_field_type['table_name']} type ON type.id=f.type_id
            INNER JOIN {meta_field_control['table_name']} control ON control.id=CASE WHEN f.control_id IS NULL THEN type.control_id ELSE f.control_id END
        WHERE t.alias=%s
        ORDER BY f.id """
    cursor.execute(sql,[table_alias])
    meta=cursor.fetchall()

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
    else:
        raise NameError("table and alias are None!")

    cursor=connection.cursor()
    cursor.execute(sql,[filter])
    meta=cursor.fetchone()
    cursor.fetchall()

    if meta==None:
        raise TableMetaDataNotFound(f"Metadata not found for table:{table_name} alias:{alias}")

    return meta




def __convert_boolean(value):
    if value=="YES": return -1
    if value=="-1": return -1
    if value=="1": return -1
    if value=="0": return 0
    if value=="NO": return 0

def __convert_field_type(field_name, value, referenced_table_id=None):
    if field_name.startswith("is_") and value.startswith("smallint") : return "boolean"
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


