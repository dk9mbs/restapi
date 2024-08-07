from services.jinjatemplate import JinjaTemplate
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from services.table_info import TableInfo
from core.meta import read_table_meta
from core.exceptions import OutDataFormatterNotFound
from core.database import Recordset
from core.context import Context
from core.exceptions import NotAllowedDataClass


class OutDataFormatter(object):
    def __init__(self, context,format_name, type_id, table_alias, data, page: int=0, page_size: int=5000):
        self._context=context
        self._page=page
        self._page_size=page_size
        self._type_id=type_id
        self._template_data={}
        self._columns={}
        self._data={}
        self._template_file=None
        self._page_mode=None

        if type(data)==Recordset:
            self._data=data.get_result()
            self._columns=self._init_columns(context, table_alias, data.get_columns())
        elif type(data)==dict:
            self._data=data
            self._columns=self._init_columns(context, table_alias,{})
        elif type(data)==list:
            self._data=data
        else:
            raise NotAllowedDataClass(f"Only Recordset or dict allowed! You give me a {type(data)}")

        self._table_info=TableInfo(context, table_alias=table_alias)
        meta=self._table_info.table_meta_data
        self._table_alias=table_alias
        self._table_id=meta['id']

        fetch=f"""
        <restapi type="select">
            <table name="api_data_formatter"/>
                <select>
                    <field name="template_header"/>
                    <field name="template_line"/>
                    <field name="template_footer"/>
                    <field name="template_file"/>
                    <field name="mime_type"/>
                    <field name="line_separator"/>
                    <field name="file_name"/>
                    <field name="content_disposition"/>
                    <field name="page_mode"/>
                </select>
            <filter type="and">
                <condition field="name" value="{format_name}" operator="="/>
                <filter type="or">
                    <condition field="table_id" value="{self._table_id}" operator="="/>
                    <condition field="table_id" value="0" operator="="/>
                    <condition field="table_id"  operator="null"/>
                </filter>
                <condition field="type_id" value="{self._type_id}" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)
        if rs.get_eof():
            raise OutDataFormatterNotFound(f"OutDataFormatter not found {format_name} for type_id {self._type_id}")

        self._page_mode=rs.get_result()[0]['page_mode']
        self._file_name=rs.get_result()[0]['file_name']
        self._content_disposition=rs.get_result()[0]['content_disposition']
        self._template_header=rs.get_result()[0]['template_header']
        self._template_line=rs.get_result()[0]['template_line']
        self._template_footer=rs.get_result()[0]['template_footer']
        self._mime_type=rs.get_result()[0]['mime_type']
        self._line_separator=rs.get_result()[0]['line_separator']
        self._template_file=rs.get_result()[0]['template_file']
        if self._template_file=="":
            self._template_file=None
        if self._line_separator=='@n':
            self._line_separator='\n'
        elif self._line_separator=='@r@n':
            self._line_separator='\r\n'

        rs.close()

    def add_template_var(self, key, value):
        self._template_data[key]=value

    def render(self):
        #table=TableInfo(self._context, table_alias=self._table_alias)
        table=self._table_info

        if self._template_file==None:
            template_header=JinjaTemplate.create_string_template(self._context,self._template_header)
            template_line=JinjaTemplate.create_string_template(self._context,self._template_line)
            template_footer=JinjaTemplate.create_string_template(self._context,self._template_footer)
        else:
            template_line=None
            template_footer=None
            template_header=JinjaTemplate.create_file_template(self._context,self._template_file)

        temp_data={"context": self._context,
                "table_alias":table.table_alias, 
                "data": self._data, 
                "columns": self._columns,
                "page":self._page, 
                "page_size": self._page_size,
                "fields": self._table_info.fields,
                "table_meta": table.table_meta_data,
                "pagemode": self._page_mode
            }

        for key, value in self._template_data.items():
            temp_data[key]=value
        result=template_header.render(temp_data)+self._line_separator

        if not template_line==None:
            temp_data={}
            for key, value in self._template_data.items():
                temp_data[key]=value

            for rec in self._data:
                temp_data['data']=rec
                temp_data['columns']=self._columns
                temp_data['table_alias']=table.table_alias
                temp_data['table_meta']=table.table_meta_data
                temp_data['page']=self._page
                temp_data['page_size']=self._page_size
                result=result+template_line.render(temp_data)+self._line_separator

        if not template_footer==None:
            temp_data={"context": self._context,
                    "table_alias": table.table_alias, 
                    "data": self._data, 
                    "columns": self._columns, 
                    "page":self._page, 
                    "page_size": self._page_size,
                    "fields": self._table_info.fields
                }
            for key, value in self._template_data.items():
                temp_data[key]=value

            result=result+template_footer.render(temp_data)

        return result

    def get_mime_type(self):
        return self._mime_type

    def get_file_name(self):
        return self._file_name

    def get_content_disposition(self):
        return self._content_disposition

    def _init_columns(self, context: Context, table_alias: str, columns: dict) -> dict():
        table=TableInfo(context, table_alias= table_alias)

        for column in columns:
            name=str(column['name'])
            name_post=""

            if name.startswith('__') and name.find('@')>=0:
                name_post=str(name[name.rfind('@')+1:]).capitalize()
                name=name[2:name.find('@')]

            if name_post!="":
                name_post=f" ({name_post})"

            column['label']=name
            
            for fld in table.fields:
                if fld['name']==name:
                    column['label']=f"{fld['label']}{name_post}"

        return columns