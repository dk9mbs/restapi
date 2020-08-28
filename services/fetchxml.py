from core.database import SelectCommandBuilder
from services.database import DatabaseServices

"""
Execute the SQL Command from a valid Cammand Builder Object
"""

def read_dataview_meta(context, alias):
    connection=context.get_connection()
    fetch=f"""
    <restapi>
        <table name="api_table"/>
        <filter type="and">
            <condition field="alias" value="{alias}" operator="="/>
        </filter>
    </restapi>
    """

    builder=SelectCommandBuilder(dict(fetch_xml=fetch))
    rs=DatabaseServices.exec(builder, context, run_as_system=True,  fetch_mode=1)
    return rs

"""
data: in case of insert or update the uploadet data as an json object
"""
def build_fetchxml_by_alias(context,alias,id=None,data=None,auto_commit=0, **kwargs):
    rs=read_dataview_meta(context,alias)
    meta=rs.get_result()
    if meta==None:
        raise ValueError("Cannot found alias %s %s" %  (alias,id))

    tmp=[]
    tmp.append("<restapi>\n")
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
