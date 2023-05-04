from .expression import Expression

class Alias(Expression):
    def __init__(self, alias: str, *args: Expression, **kwargs):
        super().__init__()
        self.logical_operator='AND'
        self.alias=''
        self._brackets=True
        self.alias=alias

        if 'logical_operator' in kwargs:
            self.logical_operator=kwargs['logical_operator']

        for arg in args:
            expression=arg.expression
            value=arg.values

            if self._expression!='' and self._expression!=None:
                self._expression=f"{self._expression} {self.logical_operator}"

            self._expression=f"{self._expression} {alias}.{expression}"
            self._values=self._values+value

        if self._brackets==True:
            self._expression=f"({self._expression})"
    """
    def __or__(self, other: Expression):
        return self._merge("OR", other)

    def __and__(self, other: Expression):
        return self._merge("AND", other)

    def _merge(self, logical_operator, other):
        a=Alias(self.alias)
        a._expression=f"({self.expression}) {logical_operator} ({other.expression})"
        a._values=self.values+other.values
        return a
    """