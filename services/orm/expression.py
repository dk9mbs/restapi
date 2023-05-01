
class WhereExpression(object):
    def __init__(self, lh: str=None, op: str=None, values=None, **kwargs):
        self._lh=lh
        self._op=op
        self._values=list()

        if values==None:
            return 
        elif isinstance(values, list):
            self._values=values
        else:
            self._values.append(values)

    def _create_expression(self) -> str:
        return f"{self._lh} {self._op} %s"

    @property
    def expression(self) -> str:
        return f"{self._lh} {self._op} %s"
        
    @property
    def values(self) -> list:
        return self._values
