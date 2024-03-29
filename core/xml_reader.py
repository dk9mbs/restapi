import xml.etree.ElementTree as ET

from core.plugin import Plugin
from core.appinfo import AppInfo
from core.context import Context

class XmlReader(object):
    """
    context........:Context
    business_case..:tag to identify in events
    globals........:global variables
    xml_bytes.....:xml as string
    """
    def __init__(self,fn_callback, context: Context,event_handler_event: str,globals: dict, xml: object) -> None:
        if type(xml)==bytes:
            self._xml=xml
        elif type(xml)==str:
            self._xml=xml
        else:
            raise Exception('You must give me a String or a bytearry')

        self._context=context
        self._fn_callback=fn_callback
        self._globals=globals
        self._event_handler_event=event_handler_event
        self._replace_node_name=dict()

    def __del__(self):
        pass

    def add_alias(self, origin_name: str, replaced_name: str) -> None:
        self._replace_node_name[origin_name]= replaced_name

    """ 
    element.: only in case of recursion
    stack...: only in case of recursion
    globals.: only in case of recursion - variables
    """
    def read(self, element: ET.Element=None, stack: dict=None, globals: dict=None) -> dict:    
        if stack==None:
            stack=dict()
            
        if globals==None:
            globals=self._globals
            globals['path']="" # xml path

        if element==None:
            """
            read the root node and start here
            """
            element=ET.fromstring(self._xml)
            self._read_childs(element, stack, globals)
        else:
            for ele in element:
                globals['path']=self._get_path(stack, ele)
                if len(ele)>0:
                    self._read_childs(ele, stack, globals)
                else:
                    self._read_item(ele, stack, globals)

        self._globals=globals
        return globals

    @property
    def xml(self):
        return self._xml

    @property
    def globals(self):
        return self._globals

    def _read_item(self, element, stack, globals) -> bool:
        plugin=Plugin(self._context, f"{globals['path']}", self._event_handler_event)
        para=self._buld_plugin_para(element, stack, globals, True)
        
        plugin.execute("before", para)
        self._fn_callback(True, element, stack, globals)
        plugin.execute("after", para)

        return True

    def _read_childs(self, element, stack: dict, globals: dict) -> bool:
        plugin=Plugin(self._context, f"{globals['path']}", self._event_handler_event)
        stack[element.tag]=element
        para=self._buld_plugin_para(element, stack, globals, False)

        plugin.execute("before", para) # call for open tag
        self._fn_callback(False, element, stack, globals)
        self.read(element, stack, globals)
        plugin.execute("after", para) # call fore close tag

        stack.pop(element.tag)
        return True

    def _buld_plugin_para(self, element: ET.Element, stack: dict, globals: dict, is_item: bool) -> dict:
        stack_tmp=dict()

        for key, value in stack.items():
            stack_tmp[key]=ET.tostring(value, encoding='unicode')

        return {"stack": stack_tmp, "element": ET.tostring(element, encoding='unicode'), "globals": globals, "is_item": is_item}

    def _get_path(self, stack: dict, element: ET.Element) -> str:
        tmp=""

        for key, value in stack.items():
            if key in self._replace_node_name:
                tmp=f"{tmp}.{self._replace_node_name[key]}"
            else:
                tmp=f"{tmp}.{key}"

        return f"{tmp}.{element.tag}"
