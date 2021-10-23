from flask import g

from core.jinjaenv import JinjaEnvironment
from core.plugin import Plugin
from core.meta import read_table_view_meta, read_table_meta
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices

#
# jinja template functions
#
def test(table_alias, viewname, query):
    context=g.context
    table_meta=read_table_meta(context,alias=table_alias)
    view_meta=read_table_view_meta(g.context, table_meta['id'], viewname, 'SELECTVIEW')
    fetchparser=FetchXmlParser(str(view_meta['fetch_xml']).replace('$$query$$',query), context)
    rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
    return rs.get_result()

def init():
    JinjaEnvironment.register_template_function('datacomboview', test)

