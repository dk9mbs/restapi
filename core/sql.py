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
def exec_raw_sql(context: Context, sql: str, params: list=[]):
    result=None
    connection=context.get_connection()
    cursor=connection.cursor()
    cursor.execute(sql,params)
    result=cursor.fetchall()
    cursor.close()

    if sql.upper().startswith('INSERT'):
        result={"inserted_id": connection.inserted_id}

    if result==[] or result==None or result==():
        return None
    
    return result