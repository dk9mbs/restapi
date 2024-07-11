import pymysql.cursors
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

from core.context import Context
from config import CONFIG
from core.log import create_logger
from core.exceptions import ConfigNotValid

"""
fetch_mode: 0=all 1=one >1 many
"""
def exec_raw_sql(context: Context, sql: str, params: list=[], fetch_mode: int=0, commit: bool=False):
    result=None
    connection=context.get_connection()
    cursor=connection.cursor()
    cursor.execute(sql,params)
    result=cursor.fetchall()
    if commit:
        connection.commit()
    cursor.close()

    if sql.strip().upper().startswith('INSERT'):
        if result!=None and result!=0 and result!='':
            return {"inserted_id": connection.insert_id()}

    if result==[] or result==None or result==():
        return None
    
    if fetch_mode==1:
        return result[0]

    return result