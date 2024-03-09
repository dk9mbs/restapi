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
from core.jsontools import merge
from core.setting import Setting
from core.context import Context

logger=log.create_logger(__name__)
#
# jinja template functions
# do not use this functions directly.
# use this functions only via jinja templates!
# The function names can by change
#
def _get_current_time(time_zone='MEZ', format='%H:%M'):
    return datetime.today().strftime(format)

def _get_current_date(time_zone='MEZ', format='%d.%m.%Y'):
    return datetime.today().strftime(format)

"""
datetime....:2023-02-10T00:00:00
format......:%m
"""
def _format_date(date_time, format_out='%m', format_in='%Y-%m-%dT%H:%M:%S'):
    d=datetime.strptime(date_time, format_in)
    return d.strftime(format_out)

def _replace (string, search, replace):
    return string.replace(search, replace)

def _ui_app_info(context):
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

def _build_query_string(context, append_args={}, **kwargs):
    if context==None:
        logger.warning(f"Deprecated!Using build_query_string with context==None! I will use g.context!")
        context=g.context
    return httphelper.build_query_string(context, append_args)

def _datacomboview(table_alias, viewname, query):
    context=g.context
    table_meta=read_table_meta(context,alias=table_alias)
    fetch_xml=f"""
    <restapi type="select">
        <table name="{ table_meta['alias'] }" alias="a"/>
        <select>
            <field name="{ table_meta['id_field_name'] }" table_alias="a" alias="id"/>
            <field name="{ table_meta['desc_field_name'] }" table_alias="a" alias="name"/>
        </select>
    </restapi>
    """
    fetchparser=FetchXmlParser(fetch_xml, context)
    rs=DatabaseServices.exec(fetchparser,context, fetch_mode=0)
    return rs.get_result()


def _image_by_path(context, path, **kwargs):
    width=""
    css_class="restapi_image"

    if 'width' in kwargs and 'unit' in kwargs:
        width=f"width: {kwargs['width']}{kwargs['unit']}"

    if 'css_class' in kwargs:
        css_class=kwargs['css_class']

    html=f"""<!-- start of jinja image(img_by_path|{path}|{width}|class:{css_class};)-->
    <a target="_blank" href="/api/v1.0/file/{path}">
    <img style="{width};" class="{css_class}" src="/api/v1.0/file/{path}"></img>
    </a>
    <!-- end of jinja image -->
    """

    return html


def _execute_fetch_xml(context, fetch_xml, run_as_system=False):
    fetchparser=FetchXmlParser(fetch_xml, context)
    rs=DatabaseServices.exec(fetchparser, context, fetch_mode=0, run_as_system=run_as_system)
    return rs

def _recordset_to_list(context, rs, fields, reverse=False):
    return DatabaseServices.recordset_to_list(context, rs, fields, reverse)

def _merge_json(json1, json2):
    return merge(json1,json2)

def _log_info(text):
    logger.info(text)

def _get_debug_level(context):
    level=int(Setting.get_value(context,"core.debug.level",0))
    return level

def _get_context():
    return g.context

def _listitems(items_string):
    result=[]
    items=items_string.split('|')

    for item in items:
        key=item.split(';')[0]
        value=item.split(';')[1]
        result.append({"key": key, "value": value})

    return result

def _escape_html(text):
    import html
    return html.escape(str(text))

def _is_item_in_dict(jsondict, key):
    if key in jsondict:
        return True

    return False

"""
Result all Fields from a tabe
used for create the datamodel with jinja for the orm mapper
"""
def _metadata_table_fields(context: Context, table_alias: str) -> dict:
    from core.meta import read_table_field_meta

    return read_table_field_meta(context, table_alias)
    pass

# Filter
def _filter_from_json(value, default={}):
    import json
    if value==None:
        return default
    else:
        return json.loads(value)

def _filter_value_from_json(json_value, name, default=None):
    #logger.info(f"{name} {json}")
    import json
    if type(json_value)==str:
        json_value=json.loads(json_value)

    if name in json_value:
        return json_value[name]

    return default

def init():
    JinjaEnvironment.register_template_function('datacomboview', _datacomboview)
    JinjaEnvironment.register_template_function('current_time', _get_current_time)
    JinjaEnvironment.register_template_function('current_date', _get_current_date)
    JinjaEnvironment.register_template_function('ui_app_info', _ui_app_info)
    JinjaEnvironment.register_template_function('build_query_string', _build_query_string)
    JinjaEnvironment.register_template_function('image_by_path', _image_by_path)
    JinjaEnvironment.register_template_function('dataquery', _execute_fetch_xml)
    JinjaEnvironment.register_template_function('recordset_to_list', _recordset_to_list)
    JinjaEnvironment.register_template_function('merge_json', _merge_json)
    JinjaEnvironment.register_template_function('log_info', _log_info)
    JinjaEnvironment.register_template_function('get_debug_level', _get_debug_level)
    JinjaEnvironment.register_template_function('get_context', _get_context)
    JinjaEnvironment.register_template_function('listitems2json', _listitems)
    JinjaEnvironment.register_template_function('format_date', _format_date)
    JinjaEnvironment.register_template_function('replace', _replace)
    JinjaEnvironment.register_template_function('escape_html', _escape_html)
    JinjaEnvironment.register_template_function('is_item_in_dict', _is_item_in_dict)
    JinjaEnvironment.register_template_function('metadata_table_fields', _metadata_table_fields)


    JinjaEnvironment.register_filter_function('from_json', _filter_from_json)
    JinjaEnvironment.register_filter_function('value_from_json', _filter_value_from_json)


