from core.database import CommandBuilderFactory


from core.database import FetchXmlParser
from config import CONFIG
from core.appinfo import AppInfo
from core.permission import Permission


AppInfo.init(__name__, CONFIG['default'])

session_id=AppInfo.login("root","password")
context=AppInfo.create_context(session_id)


print(Permission().validate(context, "read", "guest", "dummy"))

AppInfo.save_context(context, True)
AppInfo.logoff(context)


