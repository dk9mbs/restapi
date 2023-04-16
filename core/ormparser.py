#from core.exceptions import TypeNotAllowedInFieldList
#from core.meta import read_table_field_meta
from core.baseparser import BaseParser
#from services.orm.condition import Q
from services.orm.field import Field

class OrmParser(BaseParser):
    def __init__(self, sql, context, page=0, page_size=0):
        super().__init__(sql, context, page, page_size)




