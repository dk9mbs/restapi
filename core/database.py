import json
from flaskext.mysql import MySQL
import pymysql.cursors
#from mysql.connector import FieldType

from config import CONFIG
from core.fetchxmlparser import FetchXmlParser
from core.permission import Permission
from core import log
from core.jsontools import json_serial
from core.formatter_factory import FormatterFactory
from core.exceptions import WrongFetchMode

logger=log.create_logger(__name__)

class Recordset:
    def __init__(self, cursor, page_size=0, row_count=0):
        self._cursor=cursor
        self._result=None
        self._fetch_mode=0
        self._inserted_id="" # in case of insert statements
        self._page_size=page_size
        self._row_count=row_count

    def __del__(self):
        self.close()

    def get_row_count(self):
        return self._row_count

    def get_page_count(self):
        import math
        if self._page_size<=0:
            return 1
        elif self._row_count==0:
            return 0
        else:
            return int(math.ceil(self._row_count/self._page_size))

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
            raise WrongFetchMode(f"wrong fetch_mode in recordset.read: {fetch_mode} Did you mean 0(all) or 1(one)?")

    def execute_formatter(self,context, columns):
        formatters={}
        if self.get_eof():
            return

        for col in columns:
            if col['formatter'] != None and col['formatter'] != "":
                name=col['formatter']
                if not name in formatters:
                    factory=FormatterFactory(context, name)
                    formatter=factory.create()
                    formatters[name]=formatter

        if isinstance(self._result, list):
            for rec in self._result:
                self._execute_formatter(context, columns, rec, formatters)
        elif isinstance(self._result, dict):
            self._execute_formatter(context, columns, self._result, formatters)
        else:
            raise Exception('only list or dict allowed!')

    def _execute_formatter(self, context, columns, rec, formatters):
        for col in columns:
            if col['formatter'] != None and col['formatter'] != "":
                #field=col['database_field']
                field=col['alias']
                formatted_field=f"__{field}@formatted_value"
                name=col['formatter']
                formatter=formatters[name]

                rec[formatted_field]=None #init the field first!
                rec[formatted_field]=formatter.output(context, field, rec[field])

    def get_eof(self):
        if self._result==None or self._result==[] or self._result=={} or self._result==():
            return True
        else:
            return False

    def set_result(self, result):
        self._result=result

    def get_result(self):
        if(self._result==()):
            return []
        else:
            tmp=json.dumps(self._result, default=json_serial)
            data=json.loads(tmp)

            if data==None:
                return None

            if type(data) is dict:
                self._replace_none(data, None, "")
            else:
                for item in data:
                    self._replace_none(item, None, "")

            return data

    def get_cursor(self):
        return self._cursor

    def set_inserted_id(self, id):
        self._inserted_id=id

    def get_inserted_id(self):
        if self._inserted_id==None:
            return 0
        else:
            return self._inserted_id

    def get_columns(self):
        #name, type_code, display_size, internal_size, precision, scale, null_ok
        columns=[]
        if self._cursor.description == None:
            return columns

        for i in range(len(self._cursor.description)):
            desc=self._cursor.description[i]
            columns.append({"name": desc[0],
                    "type_code":desc[1],
                    "display_size":desc[2],
                    "internal_size":desc[3],
                    "precision":desc[4],
                    "scale":desc[5],
                    "allow_null":desc[6]})

        return columns

    """
    Clear the buffer
    """
    def close(self):
        if not self._cursor==None:
            self._cursor.fetchall()


    def _replace_none(self, data_dict,v,rv):
        for key in data_dict.keys():
            if data_dict[key] == v:
                data_dict[key] = rv
            elif type(data_dict[key]) is dict:
                self._replace_none(data_dict[key],v,rv)

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

