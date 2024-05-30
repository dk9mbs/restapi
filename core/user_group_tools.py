import json
import pymysql.cursors
from flask import Flask, Blueprint
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import uuid

from core.context import Context
from config import CONFIG
from core.log import create_logger
from core.exceptions import ConfigNotValid


class UserGroupTools(object):

    def __init__(self):
        pass

    @classmethod
    def delete_private_user_group(cls, context: Context, user_id: int) -> bool:
        sql=f"""
        DELETE FROM api_group WHERE user_id=%s;
        """
        cursor=context.get_connection().cursor()
        cursor.execute(sql,[user_id])
        grp=cursor.fetchone()
        cursor.fetchall()
        cursor.close()

    @classmethod
    def add_or_get_private_user_group(cls, context: Context, user_id: int) -> int:
        result=None
        connection=context.get_connection()
        sql=f"""
        SELECT id FROM api_group WHERE user_id=%s
        """
        cursor=connection.cursor()
        cursor.execute(sql,[user_id])
        grp=cursor.fetchone()
        cursor.fetchall()
        cursor.close()

        if grp==None:
            sql=f"""
            SELECT * FROM api_user WHERE id=%s;
            """
            cursor=connection.cursor()
            cursor.execute(sql,[user_id])
            user=cursor.fetchone()
            cursor.close()

            if user==None:
                raise Exception(f"User with user_id {user_id} not found")

            sql=f"""
            INSERT INTO api_group (groupname, user_id,is_admin, solution_id) VALUES (%s, %s, 0, %s);
            """
            cursor=connection.cursor()
            cursor.execute(sql,[f"~{user['username']}", user_id, 3])
            cursor.fetchall()
            cursor.close()
            result=connection.insert_id()
        else:
            result=grp['id']

        return result