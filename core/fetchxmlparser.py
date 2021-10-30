import json
import xml.etree.ElementTree as ET 
from core import log
from core.exceptions import TableAliasNotFoundInFetchXml

logger=log.create_logger(__name__)

"""

"""
class FetchXmlParser:

    def __init__(self, fetch_xml, context):
        self._logger=log.create_logger(__name__)
        self._fetch_xml=fetch_xml
        self._context=context

        self._sql_type=""
        self._sql_where=""
        self._sql_table=""
        self._sql_table_alias=""
        self._sql_table_join=""
        self._sql_select="*"
        self._sql_comment=""
        self._sql_order=""
        self._sql_paramaters_order=[]
        self._json_fields={} # for insert and update
        self._tables=[]
        self._sql_parameters_where=[]
        self._table_aliases={}
        self._columns_desc=[]
        self.parse()

    def __init_properties(self):
        self._sql_type=""
        self._sql_where=""
        self._sql_table=""
        self._sql_table_alias=""
        self._sql_table_join=""
        self._sql_select="*"
        self._sql_comment=""
        self._sql_order=""
        self._sql_paramaters_order=[]
        self._json_fields={}
        self._tables=[]
        self._sql_parameters_where=[]
        self._table_aliases={}
        self._columns_desc=[]

    def get_columns(self):
        return self._columns_desc

    def get_table_by_alias(self, alias):
        if alias in self._table_aliases:
            return self._table_aliases[alias]
        else:
            raise TableAliasNotFoundInFetchXml(f"Alias {alias} not found in fetchxml: {self._fetch_xml}")

    def get_sql_fields(self):
        return self._json_fields

    def get_sql_type(self): return self._sql_type

    def get_auto_commit(self): return False

    """
    Returns all joined tables
    """
    def get_tables(self):
        return self._tables

    """
    returns the tablename from the table node
    """
    def get_main_table(self):
        return self._sql_table

    def get_sql(self):

        if self._sql_type=="insert":
            return self.get_insert()
        elif self._sql_type=="create":
            return self.get_insert()
        elif self._sql_type=="update":
            return self.get_update()
        elif self._sql_type=="select":
            return self.get_select()
        elif self._sql_type=="read":
            return self.get_select()
        elif self._sql_type=="delete":
            return self.get_delete()
        else:
            logger.warning(self.get_select())
            raise NameError(f"unknown type in fetchxml: {self._sql_type} {self._fetch_xml}")

    def get_select(self):
        params=[]
        sql=[]
        sql.append(f"SELECT {self._sql_select} FROM {self._sql_table} {self._sql_table_alias} {self._sql_table_join} ")

        if self._sql_where != "":
            sql.append(f" WHERE {self._sql_where}")
            params=self._sql_parameters_where

        if self._sql_order != "":
            sql.append(f" ORDER BY {self._sql_order}")
            params=params+self._sql_paramaters_order

        sql.append(f"{self._sql_comment}")
        return (''.join(sql),params)

    def get_insert(self):
        fields,values, params=self._build_insert_fields()
        sql=f"INSERT INTO {self._sql_table} ({fields}) VALUES ({values}{self._sql_comment})"
        return (sql,params)

    def get_update(self):
        fields, params=self._build_update_fields()
        sql=f"UPDATE {self._sql_table} SET {fields} WHERE {self._sql_where}{self._sql_comment}"
        return (sql,params+self._sql_parameters_where)

    def get_delete(self):
        sql=f"DELETE FROM {self._sql_table} WHERE {self._sql_where}{self._sql_comment}"
        return (sql, self._sql_parameters_where)

    def parse(self):
        self.__init_properties()

        tree=ET.fromstring(self._fetch_xml)
        if 'type' in tree.attrib:
            self._sql_type=tree.attrib['type']
        else:
            raise NameError(f"No Type in xml {self._fetch_xml}")

        # create the table alias mapping
        for node in tree:
            if node.tag == "table":
                table=node.attrib['name']
                alias=table
                if "alias" in node.attrib:
                    alias=node.attrib['alias']
                self._append_alias(table, alias)
            elif node.tag == "joins":
                for join in node:
                    table=join.attrib['table']
                    alias=table
                    if "alias" in join.attrib:
                        alias=join.attrib['alias']

                    self._append_alias(table, alias)

        # read all nodes and create the sql statement
        for node in tree:
            if node.tag == "filter":
                self._sql_where=self._build_where(node)
            elif node.tag == "table":
                self._build_table(node)
            elif node.tag == "fields":
                self._build_fields(node)
            elif node.tag == "select":
                self._build_select(node)
            elif node.tag == "joins":
                self._build_join(node)
            elif node.tag == "comment":
                self._build_comment(node)
            elif node.tag == "orderby":
                self._build_order(node)


    def _escape_string(self, input, scope="somewhere"):
        not_allowed=[";","--","\0","\b","\n","\t","\r"]

        for x in not_allowed:
            if input.find(x)>-1:
                raise NameError(f"Special Chars in String: {x}")
            input=input.replace(x, "")


        return input

    def _build_update_fields(self):
        sql=[]
        parameters=[]

        for k,v in self._json_fields.items():
            if not sql==[]:
                sql.append(",")

            sql.append(f"{k}=%s")
            parameters.append(v['value'])

        return (''.join(sql), parameters)

    def _build_insert_fields(self):
        fields=[]
        values=[]
        parameters=[]

        for k,v in self._json_fields.items():
            if not fields==[]:
                fields.append(",")
                values.append(",")

            fields.append(f"{k}")
            values.append("%s")
            parameters.append(v['value'])

        return (''.join(fields),''.join(values), parameters)

    """
    <orderby>
        <field name="tablename" alias="t" sort="ASC"/>
    </orderby>
    """
    def _build_order(self, node):
        sql=[]
        for item in node:
            name=item.attrib['name']
            alias=""
            sort="ASC"
            if 'alias' in item.attrib:
                alias = item.attrib['alias']+"."
            if 'sort' in item.attrib:
                sort=item.attrib['sort']

            if sql!=[]:
                sql.append(",")

            sql.append(f"{alias}{name} {sort}")
        self._sql_order=''.join(sql)

    def _build_comment(self, node):
        if 'text' in node.attrib:
            self._sql_comment= f" /* {self._escape_string(node.attrib['text'])} */"

    """
    <joins>
        <join table="api_user_group" alias="ug" type="inner" condition="a.id=b.id"/>
    </joins>

    table=mandatory
    condition=mandatory
    """
    def _build_join(self,node):
        sql=[]
        for join in node:
            join_type="inner"
            alias=""

            table=self._escape_string(join.attrib['table'])

            if 'type' in join.attrib:
                join_type=self._escape_string(join.attrib['type'])
            if 'alias' in join.attrib:
                alias=self._escape_string(join.attrib['alias'])

            condition=self._escape_string(join.attrib['condition'])
            sql.append(f"{join_type} join {table} {alias} ON ({condition}) ")
            self._tables.append(table)

        self._sql_table_join=''.join(sql)

    def _build_table(self,node):
        table=node.attrib['name']
        self._sql_table=table
        self._tables.append(table)

        if 'alias' in node.attrib:
            self._sql_table_alias=node.attrib['alias']

    """
        <select>
            <field name="username" table_alias="u" alias="name"/>
        </select>
    """
    def _build_select(self, node):
        sql=[]
        for field in node:
            if not sql==[]:
                sql.append(",")
            table_alias=""
            alias=""

            if 'alias' in field.attrib:
                alias=self._escape_string(f"{field.attrib['alias']}")

            if 'table_alias' in field.attrib:
                table_alias=self._escape_string(f"{field.attrib['table_alias']}.")

            name=self._escape_string(field.attrib['name'])
            sql.append(f"{table_alias}{name} {alias}")
            self._build_column_header(field)

        self._sql_select=''.join(sql)


    def _build_column_header(self, field):
        name=self._escape_string(field.attrib['name'])
        column_header=name
        alias=name
        table=self._sql_table
        table_alias=""

        if 'table_alias' in field.attrib:
            table_alias=self._escape_string(field.attrib['table_alias'])
            table=self.get_table_by_alias(table_alias)['name']

        if 'alias' in field.attrib:
            alias=field.attrib['alias']
            column_header=alias

        if 'header' in field.attrib:
            column_header=filed.attrib['header']

        column_desc={"table": table, "database_field": name, "label": column_header, "alias": alias}
        self._columns_desc.append(column_desc)


    """
    Convert the xml to a json object
    """
    def _build_fields(self,node):
        fields={}

        for field in node:
            # values are replaced by execute
            # in case of no value attrib in node use None/null per default
            value=None

            if 'value' in field.attrib:
                value=field.attrib['value']
                if value == "None" or value == "null":
                    value=None

            name=self._escape_string(field.attrib['name'],"fieldname")

            fields[name]={"value": value, "old_value":None}

        self._json_fields=fields

    def _build_where(self, node):
        sql=""
        op=" AND "
        if 'type' in node.attrib:
            op=node.attrib['type']

        for item in node:
            if item.tag=="filter":
                # in case of sub filter condition
                if 'type' in item.attrib:
                    op=self._escape_string(item.attrib['type'],"operator")
                else:
                    op="AND"

                if not sql=="":
                    sql=sql+(" %s " % op)
                sql=sql+self._build_where(item)
            else:
                #op=" AND "
                operator="="
                field=self._escape_string(item.attrib['field'],"fieldname")
                # do niot escape values here. This will be done by execute
                value=""
                if 'value' in item.attrib:
                    value=item.attrib['value']

                if 'type' in item.attrib:
                    op=self._escape_string(item.attrib['type'],"operator")

                if 'alias' in item.attrib:
                    field="%s.%s" % ( self._escape_string(item.attrib['alias'],"alias"), field)

                if 'operator' in item.attrib:
                    operator=item.attrib['operator']

                if not sql=="":
                    sql=sql+(" %s " % op)

                if operator=="eq":
                    operator="="
                elif operator=="neq":
                    operator="<>"
                elif operator=="geq":
                    operator=">="
                elif operator=="leq":
                    operator="<="
                if operator == "null":
                    sql=sql+field+" IS NULL"
                elif operator == "notnull":
                    sql=sql+field+" IS NOT NULL"
                else:
                    sql=sql+field+" "+operator+" %s"
                    self._sql_parameters_where.append(value)

        #print(sql)
        return "("+sql+")"

    def _append_alias(self, table, alias=None):
        if alias==None or alias=="":
            alias=table

        #self._table_aliases.append({"table": table, "alias": alias})
        self._table_aliases[alias]={"name": table, "alias": alias}
