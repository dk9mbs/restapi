import argparse
import sys
from core.database import CommandBuilderFactory
from core.database import FetchXmlParser
from core.appinfo import AppInfo
from core.meta import build_table_fields_meta
from config import CONFIG
from core.log import create_logger

logger=create_logger(__name__)

parser = argparse.ArgumentParser(description='Build the metadata cache.')
parser.add_argument('--user','-u', type=str, help='restapi user')
parser.add_argument('--password','-p', type=str, help='restapi password')
args = parser.parse_args()

user=args.user
password=args.password

AppInfo.init(__name__, CONFIG['default'])

print(f"Host............:{AppInfo.get_current_config('mysql','host')}")
print(f"Database........:{AppInfo.get_current_config('mysql','database')}")
print(f"User............:{AppInfo.get_current_config('mysql','user')}")

session_id=AppInfo.login(args.user,args.password)
if session_id==None:
    print(f"connot log in")
    sys.exit(-1)

print(f"Session.........:{session_id}")
context=AppInfo.create_context(session_id)

build_table_fields_meta(context)

AppInfo.save_context(context, True)
AppInfo.logoff(context)


