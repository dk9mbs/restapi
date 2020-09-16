#from core.database import SelectCommandBuilder
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.meta import read_table_meta

"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def build_fetchxml_by_table_name(context,table_name,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return __build_fetchxml_by(context,None,table_name,id,data,auto_commit, type)

def build_fetchxml_by_alias(context,alias,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return __build_fetchxml_by(context,alias,None,id,data,auto_commit, type)

"""
data: in case of insert or update the uploadet data as an json object
"""
def __build_fetchxml_by(context,alias,table_name,id=None,data=None,auto_commit=0, type="select", **kwargs):
    meta=read_table_meta(context,alias=alias,table_name=table_name)
    if meta==None:
        raise NameError("%s not exists in api_table (%s)" %  (alias,id))

    tmp=[]
    tmp.append(f"<restapi type=\"{type}\">\n")
    tmp.append(f"<table name=\"{meta['table_name']}\"/>\n")

    if id!=None:
        tmp.append("<filter type=\"and\">\n")
        tmp.append(f"<condition field=\"{meta['id_field_name']}\" value=\"{id}\" operator=\"=\"/>\n")
        tmp.append("</filter>\n")

    if data!=None:
        tmp.append("<fields>\n")
        for k,v in data.items():
            tmp.append(f"<field name=\"{k}\" value=\"{v}\"/>\n")

        tmp.append("</fields>\n")
    tmp.append("</restapi>")

    return ''.join(tmp)
