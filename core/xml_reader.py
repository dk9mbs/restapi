import xml.etree.ElementTree as ET

from core.plugin import Plugin
from core.appinfo import AppInfo
from core.context import Context

class XmlReader(object):
    """
    context........:Context
    business_case..:tag to identify in events
    xml_string.....:xml as string
    """
    def __init__(self,context: Context,business_case: str, xml_string: bytearray) -> None:
        self._xml_string=xml_string
        self._context=context

    def __del__(self):
        pass

    """ 
    element.: only in case of recursion
    stack...: only in case of recursion
    """
    def read(self, element=None, stack=None):

        if stack==None:
            stack=dict()

        if element==None:
            """
            read the root node and start here
            """
            element=ET.fromstring(self._xml_string)
            print(f"{element.tag}")
            self._read(element, stack)
        else:
            for ele in element:
                if len(ele)>0:
                    print(f"{ele.tag} {stack}")
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


if __name__=="__main__":
    from config import CONFIG
    AppInfo.init(__name__, CONFIG['default'])
    session_id=AppInfo.login("root","password")
    context=AppInfo.create_context(session_id)

    f=open('/tmp/test.idoc','rb')
    idoc=f.read()
    f.close()

    reader=XmlReader(context, "SAP-DELIVERY01", idoc)
    reader.read()
