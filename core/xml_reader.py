import xml.etree.ElementTree as ET

from core.plugin import Plugin
from config import CONFIG
from core.appinfo import AppInfo
from core.context import Context

class XmlReader(object):
    def __init__(self,context: Context, idoc: str) -> None:
        self._idoc=idoc
        self._context=context

    def read(self, element=None, stack=None):

        if stack==None:
            stack=dict()

        if element==None:
            tree=ET.fromstring(self._idoc)
            element=tree[0]
            print(element)

        for ele in element:
            if len(ele)>0:
                plugin=Plugin(self._context, f"xmlreader_{ele.tag}", "read")
                plugin.execute("before", stack)

                stack[ele.tag]=ele
                self.read(ele, stack)
                stack.pop(ele.tag)
            else:
                print(f"{ele.tag} {ele.text} {stack}")



AppInfo.init(__name__, CONFIG['default'])
session_id=AppInfo.login("root","password")
context=AppInfo.create_context(session_id)

f=open('/tmp/test.idoc','rb')
idoc=f.read()
f.close()

reader=XmlReader(context, idoc)
reader.read()
