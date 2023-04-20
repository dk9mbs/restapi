from services.numerictools import isnumeric

class Field:
    def __init__(self, name=None, value=None):
        self._name=name

        if value==None:
            self._value=None
        else:
            self._value=self.convert(value)
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value) -> None:
        self._name=value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value) -> None:
        if value==None:
            self._value=None
        else:
            self._value=self.convert(value)

    def convert(self, value):
        return str(value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.data_type})>"


class StringField(Field):
    def convert(self, value):
        return value

class NumericField(Field):
    def convert(self, value):
        if not isnumeric(value):
            raise ValueError(f"{self._name} {value} is not a numeric value!")

        return value


    
class BoolField(Field):
    def convert(self, value: int) -> bool:
        if not isnumeric(value) and not isinstance(value, bool):
            raise ValueError(f"{self._name} {value} is not a bool value!")

        if value==0:
            result=False
        else:
            result=True    

        return result
    
        