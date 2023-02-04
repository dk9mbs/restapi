from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.meta import read_table_meta

"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def build_fetchxml_by_table_name(context,table_name,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return __build_fetchxml_by(context,None,table_name,None,id,data,auto_commit, type)

def build_fetchxml_by_alias(context,alias,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return __build_fetchxml_by(context,alias,None,None,id,data,auto_commit, type)

def build_fetchxml_lookup(context,alias,auto_commit=0, filter_field_name=None, filter_value=None):
    return __build_fetchxml_by(context,alias,None,None,None,None,auto_commit,"select",filter_field_name,filter_value)

def build_fetchxml_by_id(context,table_id,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return __build_fetchxml_by(context,None,None,table_id,id,data,auto_commit, type)

"""
data: in case of insert or update the uploadet data as an json object
"""
def __build_fetchxml_by(context,alias,table_name,table_id=None,id=None,data=None,auto_commit=0,
        type="select",filter_field_name=None, filter_value=None, **kwargs):
    meta=read_table_meta(context,alias=alias,table_name=table_name,table_id=table_id)
    if meta==None:
        raise NameError("%s not exists in api_table (%s)" %  (alias,id))

    tmp=[]
    tmp.append(f"<restapi type=\"{type}\">\n")
    tmp.append(f"<table name=\"{meta['table_name']}\"/>\n")

    if filter_field_name!=None:
        tmp.append("<filter type=\"and\">\n")
        tmp.append(f"<condition field=\"{filter_field_name}\" value=\"{filter_value}\" operator=\"=\"/>\n")
        tmp.append("</filter>\n")

    if id!=None:
        tmp.append("<filter type=\"and\">\n")
        tmp.append(f"<condition field=\"{meta['id_field_name']}\" value=\"{id}\" operator=\"=\"/>\n")
        tmp.append("</filter>\n")

    if data!=None:
        tmp.append("<fields>\n")
        for k,v in data.items():
            if v==None:
                tmp.append(f"""<field name="{k}"/>\n""")
            else:
                #tmp.append(f"""<field name="{k}" value="{v}"/>\n""")
                tmp.append(f"""<field name="{k}">\n""")
                tmp.append(f"""<value><![CDATA[{v}]]></value>\n""")
                tmp.append(f"""</field>\n""")

        tmp.append("</fields>\n")
    tmp.append("</restapi>")

    return ''.join(tmp)
