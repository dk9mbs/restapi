from flask import g
from datetime import datetime

from core.jinjaenv import JinjaEnvironment
from core.plugin import Plugin
from core.meta import read_table_view_meta, read_table_meta
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from services.fetchxml import build_fetchxml_by_alias
from ui.core import httphelper
from core import log

logger=log.create_logger(__name__)
#
# jinja template functions
# do not use this functions directly.
# use this functions only via jinja templates!
#
def __get_current_time(time_zone='MEZ', format='%H:%M'):
    return datetime.today().strftime(format)

def __get_current_date(time_zone='MEZ', format='%d.%m.%Y'):
    return datetime.today().strftime(format)

def __ui_app_info(context):
    app_id=context.get_arg("app_id", 1)
    fetch=build_fetchxml_by_alias(context,"api_ui_app",app_id)
    fetchparser=FetchXmlParser(fetch, context)
    rs_app=DatabaseServices.exec(fetchparser, context,run_as_system=True, fetch_mode=1)

    fetch=f"""
    <restapi type="select">
        <table name="api_ui_app_nav_item" alias="a"/>
        <select>
            <field name="id" table_alias="a"/>
            <field name="name" table_alias="a"/>
            <field name="url" table_alias="a"/>
            <field name="type_id" table_alias="a"/>
        </select>

        <filter type="and">
            <condition field="app_id" value="{app_id}" operator="="/>
        </filter>
    </restapi>
    """
    fetchparser=FetchXmlParser(fetch, context)
    rs_items=DatabaseServices.exec(fetchparser, context,run_as_system=True, fetch_mode=0)

    return (rs_app, rs_items)

def __build_query_string(context, **kwargs):
    if context==None:
        logger.warning(f"Deprecated!Using build_query_string with context==None! I will use g.context!")
        context=g.context
    return httphelper.build_query_string(context)

def __datacomboview(table_alias, viewname, query):
    context=g.context
    table_meta=read_table_meta(context,alias=table_alias)
    view_meta=read_table_view_meta(g.context, table_meta['id'], viewname, 'SELECTVIEW')
    fetchparser=FetchXmlParser(str(view_meta['fetch_xml']).replace('$$query$$',query), context)
    rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
    return rs.get_result()


def __image_by_path(context, path, **kwargs):
    width=100
    unit="%"

    if 'width' in kwargs:
        width=kwargs['width']

    if 'unit' in kwargs:
        unit=kwargs['unit']

    html=f"""<!-- start of jinja image(img_by_path|{path}|width:{width}{unit};)-->
    <a target="_blank" style="width:{width}{unit};"
    href="/api/v1.0/file/{path}">
    <img style="width:{width}{unit};" src="/api/v1.0/file/{path}"></img>
    </a>
    <!-- end of placeholder -->
    """
    return html


def __execute_fetch_xml(context, fetch_xml):
    fetchparser=FetchXmlParser(fetch_xml, context)
    rs=DatabaseServices.exec(fetchparser, context, fetch_mode=0)
    return rs

def __recordset_to_list(context, rs, fields, reverse=False):
    return DatabaseServices.recordset_to_list(context, rs, fields, reverse)

def init():
    JinjaEnvironment.register_template_function('datacomboview', __datacomboview)
    JinjaEnvironment.register_template_function('current_time', __get_current_time)
    JinjaEnvironment.register_template_function('current_date', __get_current_date)
    JinjaEnvironment.register_template_function('ui_app_info', __ui_app_info)
    JinjaEnvironment.register_template_function('build_query_string', __build_query_string)
    JinjaEnvironment.register_template_function('image_by_path', __image_by_path)
    JinjaEnvironment.register_template_function('dataquery', __execute_fetch_xml)
    JinjaEnvironment.register_template_function('recordset_to_list', __recordset_to_list)

