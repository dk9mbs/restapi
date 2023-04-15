class F:
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'

    def __init__(self, field_name=None):
        self.sql_format = field_name

    def __add__(self, other):
        return self._combine(other, operator=self.ADD)

    def __radd__(self, other):
        return self._combine(other, operator=self.ADD, is_reversed=True)

    def __sub__(self, other):
        return self._combine(other, operator=self.SUB)

    def __rsub__(self, other):
        return self._combine(other, operator=self.SUB, is_reversed=True)

    def __mul__(self, other):
        return self._combine(other, operator=self.MUL)

    def __rmul__(self, other):
        return self._combine(other, operator=self.MUL, is_reversed=True)

    def __truediv__(self, other):
        return self._combine(other, operator=self.DIV)

    def __rtruediv__(self, other):
        return self._combine(other, operator=self.DIV, is_reversed=True)

    def _combine(self, other, operator, is_reversed=False):
        f_obj = F()
        part_left = self.sql_format
        part_right = other.sql_format if isinstance(other, F) else other
        if is_reversed:
            part_left, part_right = part_right, part_left
        f_obj.sql_format = f'{part_left} {operator} {part_right}'
        return f_obj


