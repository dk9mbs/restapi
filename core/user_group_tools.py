import json
import pymysql.cursors
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

from core.context import Context
from core.log import create_logger
from core.exceptions import ConfigNotValid
from core.sql import exec_raw_sql

class UserGroupTools(object):

    def __init__(self):
        pass

    @classmethod
    def add_record_permission(cls, context: Context, table_id: int, user_id: int, 
            record_id, read: bool=True, update:bool=False, delete: bool=False):

        group_id=UserGroupTools.add_or_get_private_user_group(context, user_id)

        field_record_id="record_id_int"

        sql=f"""
        INSERT INTO api_group_rec_permission (table_id, group_id, {field_record_id}, mode_read, mode_update, mode_delete)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return exec_raw_sql(context, sql, [table_id, group_id,record_id, read*-1, update*-1, delete*-1])['inserted_id']

    @classmethod
    def delete_private_user_group(cls, context: Context, user_id: int) -> bool:
        sql="""
        SELECT * FROM api_group WHERE user_id=%s;
        """
        groups=exec_raw_sql(context, sql, [user_id])

        for group in groups:
            sql=f"""
            DELETE FROM api_user_group WHERE group_id=%s AND user_id=%s;
            """
            exec_raw_sql(context, sql,[group['id'], user_id])

            sql="""
            DELETE FROM api_group_rec_permission WHERE group_id=%s;
            """
            exec_raw_sql(context, sql, [group['id']])


        sql=f"""
        DELETE FROM api_group WHERE user_id=%s;
        """
        exec_raw_sql(context, sql,[user_id])

    @classmethod
    def add_or_get_private_user_group(cls, context: Context, user_id: int) -> int:
        result=None
        connection=context.get_connection()
        sql=f"""
        SELECT id FROM api_group WHERE user_id=%s
        """
        grp=exec_raw_sql(context, sql,[user_id], fetch_mode=1)

        if grp==None:
            sql=f"""
            SELECT * FROM api_user WHERE id=%s;
            """
            user=exec_raw_sql(context,sql,[user_id], fetch_mode=1)

            if user==None:
                raise Exception(f"User with user_id {user_id} not found")

            sql=f"""
            INSERT INTO api_group (groupname, user_id,is_admin, solution_id) VALUES (%s, %s, 0, %s);
            """
            inserted_id=exec_raw_sql(context, sql, [f"~{user['username']}", user_id, 3])['inserted_id']
            result=inserted_id
            
            sql=f"""
            INSERT INTO api_user_group (user_id, group_id, solution_id)
            VALUES (%s,%s,%s)
            """
            exec_raw_sql(context, sql, [user_id, inserted_id,3 ])

        else:
            result=grp['id']

        return result