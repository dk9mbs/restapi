from core.baseparser import BaseParser
from services.orm.field import Field
from core import log
from core.exceptions import TypeNotAllowedInFieldList
from core.meta import read_table_field_meta
from core.context import Context
from core.baseparser import BaseParser
from services.orm.field import Field
from services.orm.expression import WhereExpression, Expression

class OrmParser(BaseParser):
    def __init__(self, sql, context, page=0, page_size=0):
        super().__init__(sql, context, page, page_size)

        self._where=sql['where']
        self._fields=sql['fields']
        self._main_table=sql['main_table']
        self._main_table_alias=sql['main_table_alias']
        self._orderby=sql['orderby']
        self._data=sql['data']
        self._query_vars=[]
        self._query_vars_local=[]
        self._sql_type=sql['sql_type']
        self._context=context

        vars=sql['query_vars']
        for var in vars:
            self._query_vars.append(self._nz(var))

        self._add_fields(self._main_table)

    def get_sql_fields(self):
        result={}
        for key, value in self._data.items():
            result[key]={}
            result[key]['value']=value

        return result

    def get_select(self):
        return (self._get_sql("SELECT"), self._query_vars)

    def get_sql(self, ignore_paging=False):
        return (self._get_sql(ignore_paging=ignore_paging), self._query_vars_local + self._query_vars)

    def _get_sql(self, sql_type: str=None, ignore_paging: bool=False) -> str:
        if sql_type==None:
            sql_type=self._sql_type

        if sql_type.upper()=='SELECT':
            if ignore_paging==True:
                sql=f"SELECT COUNT(*) AS cnt FROM {self._main_table} AS {self._main_table_alias} {self._main_table_join} "
            else:
                sql=f"SELECT {self._fields} FROM {self._main_table} AS {self._main_table_alias} {self._main_table_join} "

            if self._where!='':
                sql=f"{sql} WHERE {self._where}"
            if self._orderby!='':
                sql=f"{sql} ORDER BY {self._orderby}"
        elif sql_type.upper()=='INSERT':

            sql_values=""
            for key, value in self._data.items():
                if sql_values=="":
                    sql_values="%s"
                else:
                    sql_values=f"{sql_values},%s"

            sql=f"INSERT INTO {self._main_table} ({','.join(self._data)}) VALUES ({sql_values})"

        elif sql_type.upper()=='UPDATE':

            sql=f"UPDATE {self._main_table} set "
            sql=sql+",".join(f"{key}=%s" for key, value in self._data.items())

            for key, value in self._data.items():
                self._query_vars_local.append(self._nz(value))

            sql=f"{sql} WHERE {self._where}"
        elif sql_type.upper()=='DELETE':
            sql=f"DELETE FROM {self._main_table} WHERE {self._where}"

        return sql


    """
    table.........: table alias from restapi
    """
    def _add_fields(self, table: str):
        meta_fields=read_table_field_meta(self._context, table)

        fields=""
        tmp=[]
        sql_join=[]
        self._columns_desc=[]

        for field in meta_fields:
            if field['is_virtual']==0:
                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": field['name'], "formatter": None}
                self._columns_desc.append(column_desc)

                if tmp != []:
                    tmp.append(",")

                tmp.append(f"{self._main_table_alias}.{ field['name'] } AS { field['name'] } ")

            if field['is_lookup']==-1 and field['referenced_table_desc_field_name']!=None:
                if tmp != []:
                    tmp.append(",")

                ref_alias=f"{ field['name'] }_{ field['referenced_table_name'] }_{ field['referenced_field_name'] }"
                sql_join.append(f"""LEFT JOIN { field['referenced_table_name'] } AS { ref_alias } """)
                sql_join.append(f"ON {self._main_table_alias}.{ field['name'] }={ ref_alias }.{ field['referenced_field_name'] } ")

                # set the id name
                f=f"{ref_alias}.{ field['referenced_table_desc_field_name'] }"
                if fields!='':
                    fields=f"{fields},"
                fields=f"{fields}{f} AS {field['name']}_name"
                tmp.append(f"{f} AS \"__{ field['name'] }@name\", ")

                # set the url field
                f=f"CONCAT('/api/v1.0/data/{ field['referenced_table_name'] }/', { table }.{ field['name'] })"
                if fields!='':
                    fields=f"{fields},"
                fields=f"{fields}{f} AS {field['name']}_url"
                tmp.append(f"{f}  AS \"__{ field['name'] }@url\" ")

                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": f"__{field['name']}@name", "formatter": None}
                self._columns_desc.append(column_desc)
                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": f"__{field['name']}@url", "formatter": None}
                self._columns_desc.append(column_desc)


        self._fields=f"{self._fields}, {''.join(tmp)}"
        self._main_table_join=''.join(sql_join)

        for field in meta_fields:
            if fields!='':
                fields=f"{fields},"

            if field['is_virtual']==0:
                fields=f"{fields}{self._main_table_alias}.{field['field_name']} AS {field['name']}"
            else:
                fields=f"{fields} null AS {field['name']}"

        self._fields=fields


