#from core.database import SelectCommandBuilder
from services.database import DatabaseServices
from core.fetchxmlparser import FetchXmlParser

"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def read_dataview_meta(context, alias):
    connection=context.get_connection()
    fetch=f"""
    <restapi type="select">
        <table name="api_table"/>
        <comment text="{context.get_username()} system"/>
        <filter type="and">
            <condition field="alias" value="{alias}" operator="="/>
        </filter>
    </restapi>
    """
    fetchparser=FetchXmlParser(fetch)
    rs=DatabaseServices.exec(fetchparser, context, run_as_system=True,  fetch_mode=1)
    return rs

"""
data: in case of insert or update the uploadet data as an json object
"""
def build_fetchxml_by_alias(context,alias,id=None,data=None,auto_commit=0, type="select", **kwargs):
    rs=read_dataview_meta(context,alias)
    meta=rs.get_result()
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
