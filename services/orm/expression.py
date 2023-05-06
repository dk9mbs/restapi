class Expression(object):
    def __init__(self, *args, **kwargs):
        self._values=list()
        self._expression=''
        self._args=args
        self._kwargs=kwargs
        #self._expression=self._build_expression()


    @property
    def expression(self) -> str:
        return self._build_expression()
        
    @property
    def values(self) -> list:
        return self._values

    """ 
    to overrite
    """
    def _build_expression(self) -> str:
        return self._expression

    def add_expression(self, expression: str, logical_operator: str="AND", values: list=[]) -> None:
        if self._expression!='':
            self.expression=f"{self._expression} {logical_operator}"
        
        self._values=self._values+values
        self._expression=f"{self._expression} {expression}"
    
    def __or__(self, other):
        return self._merge("OR", other)

    def __and__(self, other):
        return self._merge("AND", other)

    def _merge(self, logical_operator, other):
        a=Expression(self.alias)
        a._expression=f"({self.expression}) {logical_operator} ({other.expression})"
        a._values=self.values+other.values
        return a



class WhereExpression(Expression):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self._lh=args[0]
        self._op=args[1]
        self._values=list()
        self._expression=''

        values=args[2]

        if values==None:
            return 
        elif isinstance(values, list):
            self._values=values
        else:
            self._values.append(values)

        #self._expression=self._create_expression()

    def _build_expression(self) -> str:
        return f"{self._lh} {self._op} %s"


class OrderByExpression(Expression):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._order_by=args[0]
        self._sort=args[1]

        #self._create_expression()

    def _build_expression(self) -> str:
        return f"{self._order_by} {self._sort}"