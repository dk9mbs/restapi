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
