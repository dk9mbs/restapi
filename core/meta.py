from core.exceptions import DataViewNotFound, TableMetaDataNotFound

def read_table_view_meta(context, table_id, view_name):
    connection=context.get_connection()
    filter=[table_id,view_name]

    sql=f"""
    SELECT * FROM api_table_view WHERE table_id=%s and name=%s
    """

    cursor=connection.cursor()
    cursor.execute(sql,filter)
    meta=cursor.fetchone()
    cursor.fetchall()

    if meta==None:
        raise DataViewNotFound(f"View {view_name} notfound for table_id {table_id}")

    return meta



"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def read_table_meta(context, alias=None, table_name=None):
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
    else:
        raise NameError("table and alias are None!")

    cursor=connection.cursor()
    cursor.execute(sql,[filter])
    meta=cursor.fetchone()
    cursor.fetchall()

    if meta==None:
        raise TableMetaDataNotFound(f"Metadata not found for table:{table_name} alias:{alias}")

    return meta

