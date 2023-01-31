from services.jinjatemplate import JinjaTemplate
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core.meta import read_table_meta

class DataFormatter(object):
    def __init__(self, context,format_name, table_alias, data):
        self._context=context
        self._data=data

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
        </select>
        <filter type="and">
        <condition field="name" value="{format_name}" operator="="/>
        <condition field="table_id" value="{self._table_id}" operator="="/>
        </filter>
        </restapi>
        """
        fetchparser=FetchXmlParser(fetch, self._context)
        rs=DatabaseServices.exec(fetchparser, self._context,run_as_system=True, fetch_mode=0)

        self._template_header=rs.get_result()[0]['template_header']
        self._template_line=rs.get_result()[0]['template_line']
        self._template_footer=rs.get_result()[0]['template_footer']

        rs.close()

    def render(self):
        template=JinjaTemplate.create_string_template(self._context,self._template_line)

        result=""
        for rec in self._data:
            result=result+template.render({"data": rec})

        return result

