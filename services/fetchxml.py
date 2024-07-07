from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser
from core.meta import read_table_meta, read_table_field_meta

"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def build_fetchxml_by_table_name(context,table_name,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return _build_fetchxml_by(context,None,table_name,None,id,data,auto_commit, type, None,None,[], **kwargs)

def build_fetchxml_by_alias(context,alias,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return _build_fetchxml_by(context,alias,None,None,id,data,auto_commit, type)

def build_fetchxml_lookup(context,alias,auto_commit=0, filter_field_name=None, filter_value=None,fields_select=[], **kwargs):
    return _build_fetchxml_by(context,alias,None,None,None,None,auto_commit,"select",
        filter_field_name,filter_value,fields_select=fields_select, **kwargs)

def build_fetchxml_by_id(context,table_id,id=None,data=None,auto_commit=0, type="select", **kwargs):
    return _build_fetchxml_by(context,None,None,table_id,id,data,auto_commit, type)

def build_fetchxml_referenced_records(context,alias,auto_commit=0,record_id=0, ref_table_alias="api_document",  **kwargs):
    return _build_fetchxml_by(context,alias,None,None,None,None,auto_commit,"select",
        None,None,None, record_id=record_id, ref_table_alias=ref_table_alias)


"""
data: in case of insert or update the uploadet data as an json object
"""

def _build_fetchxml_by(context,alias,table_name,table_id=None,id=None,data=None,auto_commit=0,
        type="select",filter_field_name=None, filter_value=None,fields_select=[], **kwargs):
    
    if fields_select==None:
        fields_select=[]

    meta=read_table_meta(context,alias=alias,table_name=table_name,table_id=table_id)
    #
    record_id=None
    ref_table_alias=None
    if 'record_id' in kwargs:
        record_id=kwargs['record_id']
        ref_table_alias=kwargs['ref_table_alias']
    #
    if meta==None:
        raise NameError("%s not exists in api_table (%s)" %  (alias,id))

    tmp=[]
    tmp.append(f"<restapi type=\"{type}\">\n")
    #tmp.append(f"<table name=\"{meta['table_name']}\"/>\n") # don't use the table name here!!!
    tmp.append(f"<table name=\"{meta['alias']}\"/>\n") #use alwasy the alias!!!

    if fields_select!=None and fields_select!=[]:
        tmp.append("<select>")
        for field in fields_select:
            tmp.append(f"<field name=\"{ field }\"/>")
        tmp.append("</select>")

    # show only referenced records
    if record_id!=None and ref_table_alias!=None:
        tmp.append("""<joins>\n""")
        tmp.append(f"""<join table="api_record_reference" alias="xyz" type="inner" condition="d.id=xyz.record_id"/>\n""")
        tmp.append("""</joins>\n""")
    # end show only referenced records

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
