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
        return ""

    def __or__(self, other):
        return self._merge("OR", other)

    def __and__(self, other):
        return self._merge("AND", other)

    def _merge(self, logical_operator, other):
        a=Expression()
        a._expression=f"({self.expression}) {logical_operator} ({other.expression})"
        a._values=self.values+other.values
        return a



class WhereExpression(Expression):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self._lh=""
        self._op=""
        self._values=list()
        self._expression=''

        values=None

        if len(args)==3:
            self._lh=args[0]
            self._op=args[1]
            values=args[2]
            self._expression=self._build_expression()

        if values==None:
            return 
        elif isinstance(values, list):
            self._values=values
        else:
            self._values.append(values)

    def _build_expression(self) -> str:
        if self._lh=="" or self._op=="":
            return ""

        return f"{self._lh} {self._op} %s"

    def _merge(self, logical_operator, other):
        a=WhereExpression()
        a._values=self.values+other.values

        if self.expression=="":
            a._expression=f"({other.expression})"
        else:
            a._expression=f"({self.expression}) {logical_operator} ({other.expression})"

        return a


class OrderByExpression(Expression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._order_by=args[0]
        self._sort=args[1]

    def _build_expression(self) -> str:
        return f"{self._order_by} {self._sort}"