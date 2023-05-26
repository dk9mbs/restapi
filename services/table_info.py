from core.context import Context
from core.exceptions import TableMetaDataNotFound
from core.meta import read_table_meta, read_table_field_meta

class TableInfo(object):
    def __init__(self, context: Context, table_name: str=None, table_alias: str=None, table_id: str=None) -> None:
        row=read_table_meta(context,table_alias, table_name, table_id)
        self._context=context
        self._table_name=row['table_name']
        self._table_id=row['id']
        self._table_alias=row['alias']
        self._id_field_name=row['id_field_name']
        self._id_field_type=row['id_field_type']
        self._id_field_type=row['desc_field_name']
        self._enable_audit_log=row['enable_audit_log']
        self._solution_id=row['solution_id']


    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def table_alias(self) -> str:
        return self._table_alias

    @property
    def table_id(self) -> int:
        return self._table_id

    @property
    def fields(self):
        return read_table_field_meta(self._context, table_id=self._table_id)