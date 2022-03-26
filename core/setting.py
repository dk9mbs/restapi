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


class Setting(object):

    def __init__(self):
        pass

    @classmethod
    def get_value(cls, context, setting, default_value=''):
        sql=f"""
        SELECT value FROM api_setting WHERE setting=%s
        """

        connection=context.get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,[setting])
        setting=cursor.fetchone()
        cursor.fetchall()
        cursor.close()

        if setting==None:
            return default_value
        else:
            return setting['value']
