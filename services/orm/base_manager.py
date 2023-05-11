from core import log
from core.exceptions import TypeNotAllowedInFieldList
from core.meta import read_table_field_meta
from core.context import Context
from core.ormparser import OrmParser
from core.baseparser import BaseParser
from services.database import DatabaseServices
from .expression import OrderByExpression

from .field import Field
from .expression import WhereExpression, Expression

class BaseManager:
    context=None
    
    def __init__(self,  model_class):
        self.model_class = model_class
        #self._context=context

        self._sql_type='SELECT'
        self._main_table=''
        self._main_table_alias=''
        self._where=''
        self._query_vars=[]
        self._orderby=''
        self._fields=''
        self._main_table_join=''
        self._data={} # data for update and insert

    @classmethod
    def bind(cls, context: Context) -> None:
        cls.context=context

    #def __get_sql(self, ignore_paging: bool=True) -> str:
    #    if self._sql_type.upper()=='SELECT':
    #        sql=f"SELECT {self._fields} FROM {self._main_table} AS {self._main_table_alias} {self._main_table_join} "
    #        if self._where!='':
    #            sql=f"{sql} WHERE {self._where}"
    #        if self._orderby!='':
    #            sql=f"{sql} ORDER BY {self._orderby}"
    #    elif self._sql_type.upper()=='INSERT':
    #        sql=f"INSERT INTO {self._main_table} ({','.join(self._data)}) VALUES ({','.join(self._data.values())})"
    #    elif self._sql_type.upper()=='UPDATE':
    #        sql=f"UPDATE {self._main_table} set {','.join(f'{key}={value}' for key, value in self.data.items())} WHERE {self._where}"
    #    elif self._sql_type.upper()=='DELETE':
    #        sql=f"DELETE FROM {self._main_table} WHERE {self._where}"
    #    print (sql)
    #    return sql
    
    """
    fields......: not used
    """
    def select(self, fields: list=[]):
        self._sql_type="SELECT"
        self.__set_table(self.model_class.Meta.table_name)
        #self.__add_fields(self._main_table)
        return self

    def insert(self, data: dict):
        self._sql_type="INSERT"
        self.__set_table(self.model_class.Meta.table_name)
        self._data=data

        for key, value in self._data.items():
            self._data[key]="%s"
            self._query_vars.append(value)

        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=0)
        return rs

    def update(self,primary_key: Expression, data: list):
        self._sql_type="UPDATE"
        self.__set_table(self.model_class.Meta.table_name)
        self._data=data
        self.where(primary_key)
        #print(f"*******{primary_key.expression}")
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=0)
        return rs

    def delete(self):
        self._sql_type="DELETE"
        self.__set_table(self.model_class.Meta.table_name)
        return self


    """
    obj......................:WhereExpression or Alias
    logical_operator.........:and or or (in case of q is a list)
    """
    def where(self, obj: object(), logical_operator='and'):
        values=list()
        expression=''
        if isinstance(obj, Expression):
            expression=obj.expression
            value=obj.values
            if isinstance(value, list):
                values=values+value
            else:
                values.append(value)
        else:
            raise ValueError('Obj must be a Expression')

        if self._where!='':
            self._where=f"{self._where} {logical_operator}"

        self._where=f"{self._where} {expression}"
        self._query_vars=self._query_vars+values

        return self

    def orderby(self, order_by: OrderByExpression):
        if self._orderby!='':
            self._orderby=f"{self._orderby},"

        self._orderby=f"{self._orderby}{order_by.expression}"
        return self

    """
    Return Methods
    """
    def to_list(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=0)

        model_list=[]
        for item in rs.get_result():
            model_list.append(self.model_class(**item))

        return model_list

    def to_entity(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=1)
        if rs.get_eof():
            return None
        else:
            return self.model_class(**rs.get_result())

    def to_recordset(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=0)
        return rs

    def execute(self):
        parser=self.__execute()
        rs=DatabaseServices.exec (parser, self.context, run_as_system=False, fetch_mode=0)
        return None

    """
    private methods
    """
    def __execute(self) -> BaseParser:
        info={"where": self._where,
        "fields":self._fields,
        "main_table":self._main_table,
        "main_table_alias": self._main_table_alias,
        "orderby": self._orderby,
        "data":self._data,
        "query_vars": self._query_vars,
        "sql_type": self._sql_type}

        parser=OrmParser(info, self.context)
        return parser

    def __add_default_join(self):
        pass

    def __set_table(self, table, alias=None):
        self._main_table=self.model_class.Meta.table_name
        self._main_table_alias=self.model_class.Meta.table_name


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



