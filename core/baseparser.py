from core.exceptions import TypeNotAllowedInFieldList
from core.meta import read_table_field_meta
#from services.orm.condition import Condition
#from services.orm.field import Field

class BaseParser:
    def __init__(self, sql, context, page=0, page_size=0):
        self._context=context

        self._sql=sql
        self._sql_type='SELECT'
        self._main_table=''
        self._main_table_alias=''
        self._tables=[]
        self._where=''
        self._query_vars=[]
        self._orderby=''
        self._fields=''
        self._main_table_join=''
        self._auto_commit=False
        self._table_aliases={}

    def _get_record_permission_clause(self, where_clause: str):
        if where_clause.find('api_fn_rec_permission')>=0:
            return where_clause

        result=""
        for key, value in self._table_aliases.items():
            if result != "":
                result=f"{result} AND "

            if value['meta']['enable_record_permission']!=0:
                result=f"{result} api_fn_rec_permission('"+self._context.get_username()+"','"+f"{value['name']}"+"',"+f"{value['alias']}.id"+", 'READ') "

            if where_clause!="" and where_clause!=None and result!="":
                where_clause=f"({where_clause}) AND ({result})"
            else:
                where_clause=f"{where_clause}{result}"                

            return where_clause


    def get_select(self):
        return ("", [])

    def get_tables(self):
        if not self._main_table in self._tables:
            self._tables.append(self._main_table)

        return self._tables

    def set_tables(self, value: list):
        self._tables=value

    def get_main_table(self):
        return self._main_table

    def set_main_table(self, value: str):
        self._main_table=value

    def get_main_alias(self):
        return self._main_table_alias

    def set_main_alias(self, value: str):
        self._main_table_alias=value

    def get_sql_type(self):
        return self._sql_type

    def set_sql_type(self, value: str):
        self._sql_type=value

    def get_sql(self, ignore_paging=True):
        return (self._sql, self._query_vars)

    def set_sql(self, value):
        self._sql=value

    def set_paras(self, value: list):
        self._query_vars=value

    def get_sql_fields(self):
        return {'id': {'value':'2', 'old_value':None}}

    def set_sql_fields(self, value):
        pass

    def get_columns(self):
        return []

    def set_columns(self, value):
        pass

    def get_auto_commit(self):
        return self._auto_commit

    def set_auto_commit(self, value: bool):
        self._auto_commit=value

    def get_page_size(self):
        pass

    def set_page_size(self, value: int):
        pass

    def _nz(self, value, default_value: any = None):
        if value == "None" or value == "null" or value=="":
            return default_value

        return value

