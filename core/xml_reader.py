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
            element=ET.fromstring(self._idoc)
            self._read(element, stack)
        else:
            for ele in element:
                if len(ele)>0:
                    self._read(ele, stack)
                else:
                    print(f"{ele.tag} {ele.text} {stack}")


    def _read(self, element, stack: dict):
        plugin=Plugin(self._context, f"xmlreader_{element.tag}", "read")

        stack[element.tag]=element
        self.read(element, stack)
        stack.pop(element.tag)

        plugin.execute("after", stack)


AppInfo.init(__name__, CONFIG['default'])
session_id=AppInfo.login("root","password")
context=AppInfo.create_context(session_id)

f=open('/tmp/test.idoc','rb')
idoc=f.read()
f.close()

reader=XmlReader(context, idoc)
reader.read()
