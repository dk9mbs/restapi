import xml.etree.ElementTree as ET

from core.plugin import Plugin
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
            """
            read the root node and start here
            """
            element=ET.fromstring(self._idoc)
            print(f"{element.tag}")
            self._read(element, stack)
        else:
            for ele in element:
                if len(ele)>0:
                    print(f"{ele.tag}")
                    self._read(ele, stack)
                else:
                    plugin=Plugin(self._context, f"xmlreader_item_{element.tag}", "read")
                    self.read(ele, stack)
                    plugin.execute("after", stack)


    def _read(self, element, stack: dict):
        plugin=Plugin(self._context, f"xmlreader_parent_{element.tag}", "read")
        stack[element.tag]=element
        self.read(element, stack)
        stack.pop(element.tag)
        plugin.execute("after", stack)



from config import CONFIG
AppInfo.init(__name__, CONFIG['default'])
session_id=AppInfo.login("root","password")
context=AppInfo.create_context(session_id)

f=open('/tmp/test.idoc','rb')
idoc=f.read()
f.close()

reader=XmlReader(context, idoc)
reader.read()
