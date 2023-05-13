class ExpressionMethodNotImplemented(Exception):
    pass

class Expression(object):
    def __init__(self, *args, **kwargs):
        self._values=list()
        self._expression=''
        self._args=args
        self._kwargs=kwargs

    @property
    def expression(self) -> str:
        return self._expression
        
    @property
    def values(self) -> list:
        return self._values

    """ 
    to overrite
    """
    def _build_expression(self) -> str:
        raise ExpressionMethodNotImplemented()

    def __or__(self, other):
        raise ExpressionMethodNotImplemented()

    def __and__(self, other):
        raise ExpressionMethodNotImplemented()

    def _merge(self, logical_operator, other):
        raise ExpressionMethodNotImplemented()



class WhereExpression(Expression):
    def __init__(self,lh: str="", op: str="", values=None, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self._lh=lh
        self._op=op
        self._values=list()
        self._expression=''

        if lh!="" and op!="op":
            self._expression=self._build_expression()

        if values==None:
            return 
        elif isinstance(values, list):
            self._values=values
        else:
            self._values.append(values)

    @property
    def expression(self) -> str:
        return self._expression
        
    @property
    def values(self) -> list:
        return self._values

    def _build_expression(self) -> str:
        if self._lh=="" or self._op=="":
            return ""

        return f"{self._lh} {self._op} %s"

    def __or__(self, other):
        return self._merge("OR", other)

    def __and__(self, other):
        return self._merge("AND", other)

    def _merge(self, logical_operator, other):
        a=WhereExpression()
        a._values=self.values+other.values

        if self.expression=="":
            a._expression=f"({other.expression})"
        else:
            a._expression=f"({self.expression}) {logical_operator} ({other.expression})"

        return a

"""
Order By Expression
"""
class OrderByExpression(Expression):
    def __init__(self,order_by: str="", sort: str="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._expression=''
        self._args=args
        self._kwargs=kwargs
        self._order_by=order_by
        self._sort=sort
        self._expression=self._build_expression()

    @property
    def expression(self) -> str:
        return self._expression
        
    @property
    def values(self) -> list:
        return self._values

    def _build_expression(self) -> str:
        return f"{self._order_by} {self._sort}"


    def __or__(self, other):
        return self._merge(",", other)

    def __and__(self, other):
        return self._merge(",", other)

    def _merge(self, logical_operator, other):
        a=OrderByExpression()
        a._values=self.values+other.values

        if self.expression=="":
            a._expression=f"{other.expression}"
        else:
            a._expression=f"{self.expression}{logical_operator}{other.expression}"

        return a
