import xml.etree.ElementTree as ET

"""

"""
class FetchXmlParser:

    def __init__(self, fetch_xml):
        self._tables=[]
        self._fetch_xml=fetch_xml
        self._sql_where=""
        self._sql_table=""
        self._sql_table_alias=""
        self._sql_table_join=""
        self._sql_fields=""
        self._sql_fields_insert=""
        self._sql_values_insert=""
        self._sql_select="*"
        self._sql_parameters_where=[]
        self._sql_parameters_fields=[]
        self._sql_comment=""
        self._sql_order=""
        self._sql_paramaters_order=[]

    def get_tables(self):
        return self._tables

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
        sql=f"INSERT INTO {self._sql_table} ({self._sql_fields_insert}) VALUES ({self._sql_values_insert}{self._sql_comment})"
        return (sql,self._sql_parameters_fields)

    def get_update(self):
        sql=f"UPDATE {self._sql_table} SET {self._sql_fields} WHERE {self._sql_where}{self._sql_comment}"
        return (sql,self._sql_parameters_fields+self._sql_parameters_where)

    def get_delete(self):
        sql=f"DELETE FROM {self._sql_table} WHERE {self._sql_where}{self._sql_comment}"
        return (sql, self._sql_parameters_where)

    def parse(self):
        #print("xml to parse: {xml}".format(xml=self._fetch_xml))
        tree=ET.fromstring(self._fetch_xml)
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
                self.build_comment(node)
            elif node.tag == "orderby":
                self.build_order(node)

    def _escape_string(self, input, scope="somewhere"):
        not_allowed=[";","--","\0","\b","\n","\t","\r"]

        for x in not_allowed:
            if input.find(x)>-1:
                raise NameError(f"Special Chars in String: {x}")
            input=input.replace(x, "")


        return input

    """
    <orderby>
        <field name="tablename" alias="t" sort="ASC"/>
    </orderby>
    """
    def build_order(self, node):
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

    def build_comment(self, node):
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
        self._sql_table=node.attrib['name']
        self._tables.append(node.attrib['name'])
        if 'alias' in node.attrib:
            self._sql_table_alias=node.attrib['alias']

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

        self._sql_select=''.join(sql)

    def _build_fields(self,node):
        sql=""
        fields_insert=""
        values_insert=""

        for field in node:
            # values are replaced by execute
            value=""
            if 'value' in field.attrib:
                value=field.attrib['value']

            if not sql=="":
                sql=sql+","
                fields_insert=fields_insert+","
                values_insert=values_insert+","

            name=self._escape_string(field.attrib['name'],"fieldname")
            sql=sql+name+"=%s"
            fields_insert=fields_insert+name
            values_insert=values_insert+"%s"
            self._sql_parameters_fields.append(value)

        self._sql_fields=sql
        self._sql_fields_insert=fields_insert
        self._sql_values_insert=values_insert

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
                value=item.attrib['value']

                if 'type' in item.attrib:
                    op=self._escape_string(item.attrib['type'],"operator")

                if 'alias' in item.attrib:
                    field="%s.%s" % ( self._escape_string(item.attrib['alias'],"alias"), field)

                if 'operator' in item.attrib:
                    operator=item.attrib['operator']

                if not sql=="":
                    sql=sql+(" %s " % op)

                sql=sql+field+" "+operator+" %s"
                self._sql_parameters_where.append(value)
        #print(sql)
        return "("+sql+")"
