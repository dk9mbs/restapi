from .f import F

class Q:
    operations_map = {
        'eq': '=',
        'lt': '<',
        'lte': '<=',
        'gt': '>',
        'gte': '>=',
        'in': 'IN'
    }

    def __init__(self, **kwargs):
        self._sql_format_parts = list()
        self._query_vars = list()
        self._query_objects = list()
        self._alias="main"
        self._kwargs=kwargs
        self.sql_format=''
        self.build()

    def test(self, *args, **kwargs):
        print(args)
        print(kwargs)

    def build(self):
        self._sql_format_parts = list()
        self._query_vars = list()
        self._query_objects = list()

        for expr, value in self._kwargs.items():
            if '__' not in expr:
                expr += '__eq'
            field, operation_expr = expr.split('__')
            operation_str = self.operations_map[operation_expr]

            if isinstance(value, F):
                f_obj = value
                self._sql_format_parts.append(f'{field} {operation_str} {f_obj.sql_format}')
            elif isinstance(value, list):
                vars_list = value
                self._sql_format_parts.append(f'{field} {operation_str} ({", ".join(["%s"]*len(vars_list))})')
                self._query_vars += vars_list
            else:
                self._sql_format_parts.append(f'{self._alias}.{field} {operation_str} %s')
                self._query_objects.append({"field": field, "operator": operation_expr, "value": value})
                self._query_vars.append(value)

        self.sql_format = ' AND '.join(self._sql_format_parts)


    def alias(self, alias):
        self._alias=alias
        self.build()
        return self

    def get_where(self):
        return self.sql_format

    def get_query_vars(self):
        return self._query_vars



    def __or__(self, other):
        return self._merge_with(other, logical_operator='OR')

    def __and__(self, other):
        return self._merge_with(other, logical_operator='AND')

    def _merge_with(self, other, logical_operator='AND'):
        condition_resulting = Q()
        condition_resulting.sql_format = f"({self.sql_format} {logical_operator} {other.sql_format})"
        condition_resulting._query_objects = self._query_objects+other._query_objects
        condition_resulting._query_vars = self._query_vars + other._query_vars

        return condition_resulting


#class Field:
#    def __init__(self, name, data_type):
#        self.name = name
#        self.data_type = data_type
#
#    def __repr__(self):
#        return f"<{self.__class__.__name__}: {self.name} ({self.data_type})>"
