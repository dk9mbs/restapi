from .expression import WhereExpression

class Alias(object):
    def __init__(self, alias: str, *args: WhereExpression, **kwargs):
        self.expression=''
        self.values=list()
        self.logical_operator='AND'
        self.alias=''
        self._brackets=True
        self.alias=alias

        if 'logical_operator' in kwargs:
            self.logical_operator=kwargs['logical_operator']

        for arg in args:
            expression=arg.expression
            value=arg.values

            if self.expression!='' and self.expression!=None:
                self.expression=f"{self.expression} {self.logical_operator}"

            self.expression=f"{self.expression} {alias}.{expression}"
            self.values=self.values+value

        if self._brackets==True:
            self.expression=f"({self.expression})"

    def __or__(self, other: WhereExpression):
        return self._merge("OR", other)

    def __and__(self, other: WhereExpression):
        return self._merge("AND", other)

    def _merge(self, logical_operator, other):
        a=Alias(self.alias)
        a.expression=f"({self.expression}) {logical_operator} ({other.expression})"
        a.values=self.values+other.values
        return a