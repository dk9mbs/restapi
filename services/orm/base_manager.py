from core import log
from core.exceptions import TypeNotAllowedInFieldList
from core.meta import read_table_field_meta
from core.ormparser import OrmParser
from core.baseparser import BaseParser
from services.database import DatabaseServices

from .field import Field
from .alias import Alias
from .expression import WhereExpression

class BaseManager:
    context=None
    
    def __init__(self, context, model_class):
        self.model_class = model_class
        self._context=context

        self._sql_type='SELECT'
        self._main_table=''
        self._main_table_alias=''
        self._where=''
        self._query_vars=[]
        self._orderby=''
        self._fields=''
        self._main_table_join=''

    def __get_sql(self, ignore_paging=True):
        if self._sql_type.upper()=='SELECT':
            sql=f"""SELECT {self._fields} FROM {self._main_table} AS {self._main_table_alias} {self._main_table_join} """
            if self._where!='':
                sql=f"{sql} WHERE {self._where}"
            if self._orderby!='':
                sql=f"{sql} ORDER BY {self._orderby}"

        print(sql)
        return sql

    def select(self, fields: list=[], alias: str='main'):
        self._sql_type="SELECT"
        self.__set_table(self.model_class.table_name, alias)
        self.__add_fields(self._main_table, alias, fields)
        return self

    def insert(self, fields: list):
        self._sql_type="INSERT"
        self.__set_table(self.model_class.table_name)
        self.__add_fields(fields)
        return self

    def update(self, fields: list):
        self._sql_type="UPDATE"
        self.__set_table(self.model_class.table_name)
        self.__add_fields(fields)
        return self

    def delete(self):
        self._sql_type="DELETE"
        self.__set_table(self.model_class.table_name)
        return self

    """
    obj......................:WhereExpression or Alias
    logical_operator.........:and or or (in case of q is a list)
    """
    def where(self, obj: object(), logical_operator='and'):
        values=list()
        expression=''
        if isinstance(obj, WhereExpression):
            expression=obj.expression
            value=obj.values
            values.append(value)
        elif isinstance(obj, Alias):
            expression=obj.expression
            values=obj.values
        else:
            raise ValueError('Obj must be a tuple or an Alias')

        if self._where!='':
            self._where=f"{self._where} {logical_operator}"

        self._where=f"{self._where} {expression}"

        self._query_vars=self._query_vars+values
        #for var in values:
        #    print(values)
        #    self._query_vars=self._query_vars+var

        return self


    def orderby(self, o: object) :
        #if self._orderby!='':
        #    self._orderby=f"{self._orderby},"

        #self._orderby=f"{self._orderby} {o.field_name} {o.order}"
        return self

    """
    Return Methods
    """
    def to_list(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self._context, run_as_system=False, fetch_mode=0)

        model_list=[]
        for item in rs.get_result():
            model_list.append(self.model_class(**item))

        return model_list

    def to_entity(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self._context, run_as_system=False, fetch_mode=1)
        if rs.get_eof():
            return None
        else:
            return self.model_class(**rs.get_result())

    def to_recordset(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self._context, run_as_system=False, fetch_mode=0)
        return rs

    """
    private methods
    """
    def __execute(self) -> BaseParser:
        parser=OrmParser('', self._context)

        parser.set_main_table(self._main_table)
        parser.set_main_alias(self._main_table_alias)
        parser.set_sql_type(self._sql_type)
        parser.set_sql(self.__get_sql())
        parser.set_paras(self._query_vars)

        return parser

    def __add_default_join(self):
        pass

    def __set_table(self, table, alias=None):
        self._main_table=self.model_class.table_name
        self._main_table_alias=alias

    """
    table.........: table alias from restapi
    fields........: not used
    """
    def __add_fields(self, table: str,main_table_alias: str, fields: list=[]):
        meta_fields=read_table_field_meta(self._context, table)

        tmp=[]
        sql_join=[]
        self._columns_desc=[]

        for field in meta_fields:
            if field['is_virtual']==0:
                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": field['name'], "formatter": None}
                self._columns_desc.append(column_desc)

                if tmp != []:
                    tmp.append(",")

                tmp.append(f"{main_table_alias}.{ field['name'] } AS { field['name'] } ")

            if field['is_lookup']==-1 and field['referenced_table_desc_field_name']!=None:
                if tmp != []:
                    tmp.append(",")

                ref_alias=f"{ field['name'] }_{ field['referenced_table_name'] }_{ field['referenced_field_name'] }"
                sql_join.append(f"""LEFT JOIN { field['referenced_table_name'] } AS { ref_alias } """)
                sql_join.append(f"ON { main_table_alias }.{ field['name'] }={ ref_alias }.{ field['referenced_field_name'] } ")

                tmp.append(f"{ref_alias}.{ field['referenced_table_desc_field_name'] } AS \"__{ field['name'] }@name\", ")
                tmp.append(f"CONCAT('/api/v1.0/data/{ field['referenced_table_name'] }/', { main_table_alias }.{ field['name'] })  AS \"__{ field['name'] }@url\" ")

                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": f"__{field['name']}@name", "formatter": None}
                self._columns_desc.append(column_desc)
                column_desc={"table": self._main_table, "database_field": field['name'], "label": field['label'], "alias": f"__{field['name']}@url", "formatter": None}
                self._columns_desc.append(column_desc)


        #self._sql_select=''.join(tmp)
        self._fields=f"{self._fields}, {''.join(tmp)}"
        self._main_table_join=''.join(sql_join)




        fields=''
        for field in meta_fields:
            if fields!='':
                fields=f"{fields},"

            if field['is_virtual']==0:
                fields=f"{fields}{main_table_alias}.{field['field_name']}"
            else:
                fields=f"{fields} null AS {field['name']}"

        self._fields=fields


        #for field in fields:
        #    if isinstance(field, str):
        #        self._query['fields'].append({'name': field, 'value': None})
        #    elif isinstance(field, dict):
        #        self._query['fields'].append(field)
        #    else:
        #        raise TypeNotAllowedInFieldList(f"Fieldtype not allowed in fieldlist: {type(field)}")



    #def select(self, *field_names, chunk_size=2000, condition=None):
    #    if '*' in field_names:
    #        fields_format = '*'
    #        field_names = [field.name for field in self._get_fields()]
    #    else:
    #        fields_format = ', '.join(field_names)

    #    query = f"SELECT {fields_format} FROM {self.table_name}"
    #    vars = []
    #    if condition:
    #        query += f" WHERE {condition.sql_format}"
    #        vars += condition.query_vars

    #    cursor = self._get_cursor()
    #    cursor.execute(query, vars)

        # Fetch data obtained with the previous query execution and transform it into `model_class` objects.
        # The fetching is done by batches to avoid to run out of memory.
    #    model_objects = list()
    #    is_fetching_completed = False
    #    while not is_fetching_completed:
    #        rows = cursor.fetchmany(size=chunk_size)
    #        for row in rows:
    #            row_data = dict(zip(field_names, row))
    #            model_objects.append(self.model_class(**row_data))
    #        is_fetching_completed = len(rows) < chunk_size

    #    return model_objects

    #def _get_fields(self):
    #    cursor = self._get_cursor()
    #    cursor.execute(
    #        """
    #        SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s
    #        """,
    #        (self.table_name, )
    #    )
    #    data=cursor.fetchall()
    #    return [Field(name=row['column_name'], data_type=row['data_type']) for row in data]

    #@classmethod
    #def _get_cursor(cls):
    #    return cls.connection.cursor()

    #@classmethod
    #def _execute_query(cls, query, vars):
    #    cursor = cls._get_cursor()
    #    cursor.execute(query, vars)




    #def bulk_insert(self, data):
    #    # Get fields to insert [fx, fy, fz] and set values in this format [(x1, y1, z1), (x2, y2, z2), ... ] to
    #    # facilitate the INSERT query building
    #    field_names = data[0].keys()
    #    values = list()
    #    for row in data:
    #        assert row.keys() == field_names
    #        values.append(tuple(row[field_name] for field_name in field_names))

    #    # Build INSERT query and vars following documentation at
    #    # https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    #    # values_format example with 3 rows to insert with 2 fields: << (%s, %s), (%s, %s), (%s, %s) >>
    #    n_fields, n_rows = len(field_names), len(values)
    #    values_row_format = f'({", ".join(["%s"]*n_fields)})'
    #    values_format = ", ".join([values_row_format]*n_rows)

    #    fields_format = ', '.join(field_names)
    #    query = f"INSERT INTO {self.table_name} ({fields_format}) VALUES {values_format}"
    #    vars = tuple(itertools.chain(*values))

    #    # Execute query
    #    self._execute_query(query, vars)

    #def insert(self, **row_data):
    #    self.bulk_insert(data=[row_data])

    #def update(self, new_data, condition=None):
    #    # Build UPDATE query
    #    new_data_format = ', '.join([f'{field_name} = {value}' for field_name, value in new_data.items()])
    #    query = f"UPDATE {self.table_name} SET {new_data_format}"
    #    vars = []
    #    if condition:
    #        query += f" WHERE {condition.sql_format}"
    #        vars += condition.query_vars

    #    # Execute query
    #    self._execute_query(query, vars)

    #def delete(self, condition=None):
    #    # Build DELETE query
    #    query = f"DELETE FROM {self.table_name} "
    #    vars = []
    #    if condition:
    #        query += f" WHERE {condition.sql_format}"
    #        vars += condition.query_vars

        # Execute query
    #    self._execute_query(query, vars)



