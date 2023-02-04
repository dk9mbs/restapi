from services.jinjatemplate import JinjaTemplate
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core.meta import read_table_meta
from core.exceptions import OutDataFormatterNotFound

class OutDataFormatter(object):
    def __init__(self, context,format_name, type_id, table_alias, data):
        self._context=context
        self._data=data
        self._type_id=2
        self._template_data={}

        meta=read_table_meta(context, table_alias)
        self._table_alias=table_alias
        self._table_id=meta['id']

        fetch=f"""
        <restapi type="select">
            <table name="api_data_formatter"/>
                <select>
                    <field name="template_header"/>
                    <field name="template_line"/>
                    <field name="template_footer"/>
                    <field name="mime_type"/>
                </select>
            <filter type="and">
                <condition field="name" value="{format_name}" operator="="/>
                <condition field="table_id" value="{self._table_id}" operator="="/>
                <condition field="type_id" value="{self._type_id}" operator="="/>
            </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)
        if rs.get_eof():
            raise OutDataFormatterNotFound(f"OutDataFormatter not found {format_name} for type_id {self._type_id}")


        self._template_header=rs.get_result()[0]['template_header']
        self._template_line=rs.get_result()[0]['template_line']
        self._template_footer=rs.get_result()[0]['template_footer']
        self._mime_type=rs.get_result()[0]['mime_type']
        rs.close()

    def add_template_var(self, key, value):
        self._template_data[key]=value

    def render(self):
        template_header=JinjaTemplate.create_string_template(self._context,self._template_header)
        template_line=JinjaTemplate.create_string_template(self._context,self._template_line)
        template_footer=JinjaTemplate.create_string_template(self._context,self._template_footer)

        result=template_header.render({"data": self._data})

        temp_data={}
        for key, value in self._template_data.items():
            temp_data[key]=value

        for rec in self._data:
            temp_data['data']=rec
            result=result+template_line.render(temp_data)

        result=result+template_footer.render({"data": self._data})

        return result

    def get_mime_type(self):
        return self._mime_type
