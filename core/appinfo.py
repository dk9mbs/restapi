import json
import pymysql.cursors
from flask import Flask
from flask_restplus import Resource, Api, reqparse
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import uuid

from core.context import Context
from config import CONFIG

class AppInfo:
    _app=None
    _api=None
    _mysql=None
    _current_config={}
    _guest_user=None

    @classmethod
    def init(cls,name,config):
        cls._current_config=config
        cls._app=Flask(name)
        cls._app.config['MYSQL_DATABASE_USER'] = config['mysql']['user']
        cls._app.config['MYSQL_DATABASE_PASSWORD'] = config['mysql']['password']
        cls._app.config['MYSQL_DATABASE_DB'] = config['mysql']['database']
        cls._app.config['MYSQL_DATABASE_HOST'] = config['mysql']['host']
        cls._app.config['MYSQL_DATABASE_PORT'] = 3306
        cls._app.config['RESTAPI_PORT']=5000
        cls._app.config['RESTAPI_HOST']="127.0.0.1"
        cls._app.config['RESTAPI_PLUGIN_ROOT']=config['plugin']['root']
        if 'server' in config:
            if 'port' in config['server']:
                cls._app.config['RESTAPI_PORT'] = config['server']['port']
            if 'host' in config['server']:
                cls._app.config['RESTAPI_HOST'] = config['server']['host']

        cls._app.secret_key = "MySecretKey1234"
        cls._api=Api(cls._app)
        cls._mysql=MySQL(cls._app ,cursorclass=DictCursor)
        cls._mysql.connect()

    @classmethod
    def create_connection(cls, database_id=1):
        if database_id==0:
            return cls._mysql.connect()
        elif database_id==1:
            return pymysql.connect(host=cls._app.config['MYSQL_DATABASE_HOST'],
                        user=cls._app.config['MYSQL_DATABASE_USER'],
                        password=cls._app.config['MYSQL_DATABASE_PASSWORD'],
                        db=cls._app.config['MYSQL_DATABASE_DB'],
                        charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)


    @classmethod
    def get_server_port(cls):
        return int(cls._app.config['RESTAPI_PORT'])

    @classmethod
    def get_server_host(cls):
        return cls._app.config['RESTAPI_HOST']

    @classmethod
    def get_plugin_root(cls):
        return cls._app.config['RESTAPI_PLUGIN_ROOT']

    @classmethod
    def get_app(cls):
        return cls._app

    @classmethod
    def get_api(cls):
        return cls._api

    @classmethod
    def get_mysql(cls):
        return cls._mysql

    """
    Create a context object after start_session.
    """
    @classmethod
    def create_context(cls, session_id, auto_logoff=False):
        connection=cls.create_connection()

        sql=f"""
        SELECT * FROM api_session WHERE id=%s AND disabled=0
        """
        cursor=connection.cursor()
        cursor.execute(sql, [session_id])
        rest_session=cursor.fetchone()
        cursor.fetchall()

        if rest_session==None:
            raise NameError(f'Session not exists {session_id}')


        sql=f"""
        SELECT id, username from api_user WHERE id=%s
        """
        cursor.execute(sql, [rest_session['user_id']])
        system_user=cursor.fetchone()
        cursor.fetchall()

        session_values=json.loads(rest_session['session_values'].replace("'", '"'))

        ctx=Context()
        ctx.set_connection(cls.create_connection())
        ctx.set_session_values(session_values)
        ctx.set_userinfo({"user_id": system_user['id'], "username": system_user['username']})
        ctx.set_session_id(session_id)
        ctx.set_auto_logoff(auto_logoff)

        connection.commit()
        connection.close()
        return ctx

    """
    Save the session status status and commit the database connection via context.close()
    """
    @classmethod
    def save_context(cls, context, close_context=True):

        sql=f"""
        UPDATE api_session set session_values=%s,last_access_on=now() WHERE id=%s
        """

        connection=cls.create_connection()
        cursor=connection.cursor()
        cursor.execute(sql, [str(context.get_session_values()), context.get_session_id()])
        connection.commit()
        connection.close()

        if close_context:
            context.close()

    """
    Return the guest credentials
    """
    @classmethod
    def guest_credentials(cls):
        if cls._guest_user!=None:
            return cls._guest_user

        sql=f"""
        SELECT * FROM api_user WHERE username='guest';
        """
        connection=cls.create_connection()
        cursor=connection.cursor()
        cursor.execute(sql)
        guest=cursor.fetchone()
        cursor.fetchall()
        connection.close()
        cls._guest_user=guest
        return guest

    """
    Log useron and create a valid session id
    in case of wrong username or password returns None
    """
    @classmethod
    def login(cls, username, password):
        cls.__username=None

        sql=f"""
            SELECT * FROM api_user WHERE username=%s AND password=%s AND disabled=0
        """
        connection=cls.create_connection()
        cursor=connection.cursor()
        cursor.execute(sql, (username, password))
        system_user=cursor.fetchone()
        cursor.fetchall()
        if system_user==None:
            return None

        # create a server session
        session_id=str(uuid.uuid4())
        session_values={"tag": "DK9MBS"}

        sql=f"""
            INSERT INTO api_session set id=%s,session_values=%s,user_id=%s
        """

        cursor=connection.cursor()
        cursor.execute(sql, [session_id, str(session_values), system_user['id']])
        cls.__username=username
        connection.commit()
        connection.close()

        return session_id


    @classmethod
    def logoff(cls, context):
        sql=f"""
        UPDATE api_session SET disabled=-1 WHERE id=%s
        """
        connection=cls.create_connection()
        cursor=connection.cursor()
        cursor.execute(sql,[context.get_session_id()])

        cls.__username=None

        connection.commit()
        connection.close()
