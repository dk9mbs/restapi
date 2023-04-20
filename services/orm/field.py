from services.numerictools import isnumeric

class Field:
    def __init__(self, name=None, value=None):
        self._name=name
        self._value=None

    @property
    def name(self) -> str:
        return self._name
    
    @property.setter
    def name(self, value) -> None:
        self._name=value

    @property
    def value(self):
        return self.__convert_out(self._value)
    
    @property.setter
    def value(self, value : str) -> None:
        self._value=self.__convert_in(value)

    def __convert_in(self, value: str) -> str:
        return str(value)

    def __convert_out(self):
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.data_type})>"


class StringField(Field):
    def __str__(self) -> str:
        return super().__str__()
    
class NumericField(Field):

    def __convert_in(self, value) -> None:
        if not isnumeric(value):
            raise ValueError(f"{self._name} {self._value} is not a numeric value!")

        return value
    def __convert_out(self) -> str:
        if not isnumeric(self._value):
            raise ValueError(f"{self._name} {self._value} is not a numeric value!")
        
        return self._value
    
class BoolField(Field):
    def __convert_in(self, value: int) -> str:
        if value==0:
            result=False
        else:
            result=True    
        return result
    
    def __convert_out(self):
        return super().__convert_out()