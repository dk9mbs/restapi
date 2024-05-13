import argparse
import sys
import os

from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from core.appinfo import AppInfo
from core.meta_builder import build_table_fields_meta
from config import CONFIG
from core.log import create_logger
from core.database import Recordset
from services.outdataformatter import OutDataFormatter
from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core.meta import read_table_meta
import jinjainit

jinjainit.init()

def build_datamodel(context):
    table="api_table"
    view="$orm_datamodel"

    fetch=f"""
    <restapi type="select">
        <table name="api_table"/>
    </restapi>
    """
    fetchparser=FetchXmlParser(fetch, context)
    rs=DatabaseServices.exec(fetchparser, context,run_as_system=True, fetch_mode=0)

    formatter=OutDataFormatter(context,view,2, table, rs)
    formatter.add_template_var("table_meta", read_table_meta(context, alias=table))
    formatter.add_template_var("context", context)
    rs.close()
    return formatter.render()

logger=create_logger(__name__)

parser = argparse.ArgumentParser(description='Build the metadata cache.')
parser.add_argument('--user','-u', type=str, help='restapi user')
parser.add_argument('--password','-p', type=str, help='restapi password')
args = parser.parse_args()

user=args.user
password=args.password
script_dir=os.path.dirname(os.path.realpath(__file__))

AppInfo.init(__name__, CONFIG['default'])

print(f"Host............:{AppInfo.get_current_config('mysql','host')}")
print(f"Database........:{AppInfo.get_current_config('mysql','database')}")
print(f"User............:{AppInfo.get_current_config('mysql','user')}")
print(f"Script dir......:{script_dir}")

session_id=AppInfo.login(args.user,args.password)
if session_id==None:
    print(f"connot log in")
    sys.exit(-1)

print(f"Session.........:{session_id}")
context=AppInfo.create_context(session_id)

build_table_fields_meta(context)


f=open (f"{script_dir}/../shared/model.py", 'w')
f.write(build_datamodel(context))
#print(build_datamodel(context))
f.flush()
f.close()

AppInfo.save_context(context, True)
AppInfo.logoff(context)



