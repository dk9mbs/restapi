import json
import pymysql.cursors
#from flask import Flask, Blueprint
#from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import uuid

from core.context import Context
from config import CONFIG
from core.log import create_logger
from core.exceptions import ConfigNotValid
from core.sql import exec_raw_sql

class UserGroupTools(object):

    def __init__(self):
        pass

    @classmethod
    def delete_private_user_group(cls, context: Context, user_id: int) -> bool:
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
        grp=exec_raw_sql(context, sql,[user_id])

        if grp==None:
            sql=f"""
            SELECT * FROM api_user WHERE id=%s;
            """
            user=exec_raw_sql(context,sql,[user_id])

            if user==None:
                raise Exception(f"User with user_id {user_id} not found")

            sql=f"""
            INSERT INTO api_group (groupname, user_id,is_admin, solution_id) VALUES (%s, %s, 0, %s);
            """
            exec_raw_sql(context, sql, [f"~{user[0]['username']}", user_id, 3])

            result=connection.insert_id()

            sql=f"""
            INSERT INTO api_user_group (user_id, group_id, solution_id)
            VALUES (%s,%s,%s)
            """
            exec_raw_sql(context, sql, [user_id, grp[0]['groupname'],3 ])

        else:
            result=grp['id']

        return result