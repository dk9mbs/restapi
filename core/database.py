import json
from flaskext.mysql import MySQL
import pymysql.cursors

from config import CONFIG
from core.fetchxmlparser import FetchXmlParser
from core.permission import Permission
from core import log
from core.jsontools import json_serial

logger=log.create_logger(__name__)

class Recordset:
    def __init__(self, cursor):
        self._cursor=cursor
        self._result=None
        self._fetch_mode=0

    def __del__(self):
        self.close()

    """
    fetch_mode: 0=all 1=one >1 many
    """
    def read(self, fetch_mode=0):
        self._fetch_mode=fetch_mode

        if self._fetch_mode==0:
            self._result=self._cursor.fetchall()
        elif self._fetch_mode==1:
            self._result=self._cursor.fetchone()
        else:
            raise NameError(f"wrong fetch_mode: {fetch_mode}")

    def get_result(self):
        if(self._result==()):
            return []
        else:
            tmp=json.dumps(self._result, default=json_serial)
            return json.loads(tmp)

    def get_cursor(self):
        return self._cursor

    """
    Clear the buffer
    """
    def close(self):
        if not self._cursor==None:
            self._cursor.fetchall()



"""
Base Commandbuilder Class
"""
class CommandBuilder:
    def __init__(self, kwargs):
        self._sql=None
        self._auto_commit=0
        self._fetch_xml=""
        self._fetch_xml_parser=None
        self._args=kwargs
        self._sql_parameter=[]

        if 'fetch_xml' in kwargs:
            self._fetch_xml=kwargs['fetch_xml']
        elif 'fetchxml' in kwargs:
            self._fetch_xml=kwargs['fetchxml']
        else:
            raise NameError('Cannot found fetchxml in kwargs!')

        self._fetch_xml_parser=FetchXmlParser(self._fetch_xml)
        self._fetch_xml_parser.parse()
        self.build()

    def get_sql_type(self): return "undefined"

    def build(self):
        pass

    def get_sql(self):
        return (self._sql,self._sql_parameter)

    """
    
    """
    def get_tables(self):
        return self._fetch_xml_parser.get_tables()

    """
    Returns the tablename from the table node
    """
    def get_main_table(self):
        return self._fetch_xml_parser.get_main_table()

    """
    0 or 1
    """
    def get_auto_commit(self):
        return self._auto_commit

    def set_auto_commit(self,value):
        self._auto_commit=value




"""
Build an Update Command
"""
class UpdateCommandBuilder(CommandBuilder):
    def __init__(self, kwargs):
        super().__init__(kwargs)

    def get_sql_type(self): return "update"

    def build(self):
        (sql,params)= self._fetch_xml_parser.get_update()
        self._sql_parameter=params
        self._sql=sql


"""
Build an Insert Command
"""
class InsertCommandBuilder(CommandBuilder):
    def __init__(self, kwargs):
        super().__init__(kwargs)

    def get_sql_type(self): return "insert"

    def build(self):
        (sql,params)= self._fetch_xml_parser.get_insert()
        self._sql_parameter=params
        self._sql=sql


"""
Build an Delete Command
"""
class DeleteCommandBuilder(CommandBuilder):
    def __init__(self, kwargs):
        super().__init__(kwargs)

    def get_sql_type(self): return "delete"

    def build(self):
        (sql,params)= self._fetch_xml_parser.get_delete()
        self._sql_parameter=params
        self._sql=sql


"""
Returns an sql select statement
"""
class SelectCommandBuilder(CommandBuilder):
    def __init__(self, kwargs):
        super().__init__(kwargs)

    def get_sql_type(self): return "read"

    def build(self):
        (sql,params)= self._fetch_xml_parser.get_select()
        self._sql_parameter=params
        self._sql=sql


"""
SQL Command Builder Factory
"""
class CommandBuilderFactory:
    @staticmethod
    def create_command(command, *args, **kwargs):
        #command=args[0]
        builder=None
        if command=='insert':
            builder=InsertCommandBuilder(kwargs)
        elif command=='update':
            builder=UpdateCommandBuilder(kwargs)
        elif command=='delete':
            builder=DeleteCommandBuilder(kwargs)
        elif command=='select':
            builder=SelectCommandBuilder(kwargs)
        return builder

