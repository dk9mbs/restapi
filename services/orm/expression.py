
class Expression(object):
    def __init__(self):
        self._values=list()
        self._expression=''

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
        return self._expression

    def add_expression(self, expression: str, logical_operator: str="AND", values: list=[]) -> None:
        if self._expression!='':
            self.expression=f"{self._expression} {logical_operator}"
        
        self._values=self._values+values
        self._expression=f"{self._expression} {expression}"
    


class WhereExpression(Expression):
    def __init__(self, lh: str=None, op: str=None, values=None, **kwargs):
        super().__init__()

        self._lh=lh
        self._op=op
        self._values=list()
        self._expression=''

        if values==None:
            return 
        elif isinstance(values, list):
            self._values=values
        else:
            self._values.append(values)

        self._expression=self._create_expression()

    def _create_expression(self) -> str:
        return f"{self._lh} {self._op} %s"

