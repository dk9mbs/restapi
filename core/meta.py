from core.exceptions import DataViewNotFound, TableMetaDataNotFound

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
                f.control_config AS overwrite_control_config,field_name,f.is_virtual,f.is_read_only,rt.desc_field_name AS referenced_table_desc_field_name,
                rt.alias AS referenced_table_alias, type.orm_classname,
                CASE WHEN f.control_id IS NULL THEN type.control_id ELSE f.control_id END AS control_id, f.formatter
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

def create_table_relation(context, main_table_id: int, sub_table_id: int, main_record_id_int: int=0, main_record_id_str: str=None) -> dict:
    result={}
    # main = api_user (2)
    # sub  = api_user_group (4)
    sql="""
    SELECT * FROM api_table_field WHERE table_id=%s AND referenced_table_id=%s 
    AND is_lookup<>0 AND is_virtual=0
    """
    cursor=context.get_connection().cursor()
    cursor.execute(sql,[sub_table_id, main_table_id])
    meta_fields=cursor.fetchall()
    if meta_fields==None:
        return {}

    meta_table=read_table_meta(context, table_id=main_table_id)
    sql=f"""
    SELECT * FROM {meta_table['table_name']} WHERE {meta_table['id_field_name']}=%s;
    """
    cursor=context.get_connection().cursor()
    cursor.execute(sql,[main_record_id_int])
    main_record=cursor.fetchone()
    cursor.fetchall()
    cursor.close()

    for fld in meta_fields:
        result[fld['field_name']] = main_record[fld['referenced_field_name']]

    return result

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


