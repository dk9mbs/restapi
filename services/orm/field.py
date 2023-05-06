from datetime import datetime

from services.numerictools import isnumeric
from .expression import WhereExpression, OrderByExpression
#from .base_model import BaseModel

"""

kwargs:
pk................:primary key (True or False)
format............:Format String
"""
class Field:
    def __init__(self, field_name: str=None, value: object=None, **kwargs):
        self._name=field_name
        self._primary_key=False
        self._format=None
        self._changed=False
        self._table_name=None
        self._table_alias=None

        if 'format' in kwargs:
            self._format=kwargs['format']

        if 'pk' in kwargs:
            self._primary_key=kwargs['pk']

        self._value=self._validate(value)

    def bind(self, model, name: str) -> None:
        self._table_name=model.Meta.table_name
        self._table_alias=model.Meta.table_alias
        self._name=name

    @property
    def changed(self):
        return self._changed

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format=value

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
        self._value=self._validate(value)
        self._changed=True

    @property
    def formatted_value(self):
        return self._format_value(self._value, self._format)


    def desc(self):
        return OrderByExpression(f"{self._table_alias}.{self.name}", "DESC")

    def asc(self):
        return OrderByExpression(f"{self._table_alias}.{self.name}", "ASC")


    def __eq__(self, value: object) -> WhereExpression:
        return WhereExpression(f"{self._table_alias}.{self.name}", "=", value)
    
    def __lt__ (self, value) -> WhereExpression:
        return WhereExpression(f"{self._table_alias}.{self.name}", "<", value)
    
    def __gt__ (self, value) -> WhereExpression:
        return WhereExpression(f"{self._table_alias}.{self.name}", ">", value)


    """
    overwritable methods
    """
    def _validate(self, value):
        return value

    def _format_value(self, value, format: str):
        return value


    """
    System methods
    """
    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.value})>"


class StringField(Field):
    pass

class NumericField(Field):
    def _validate(self, value):
        if value==None:
            return None

        if not isnumeric(value):
            raise ValueError(f"{self._name} {value} is not a numeric value!")

        return float(value)

    def _format_value(self, value, format):
        if format==None:
            return value
        else:
            return float(format.format(value))

class IntField(NumericField):
    def _validate(self, value):
        if value==None:
            return None

        if not isnumeric(value):
            raise ValueError(f"{self._name} {value} is not a numeric value!")

        return int(float(value))

    def _format_value(self, value, format):
        return int(value)

class BoolField(Field):
    def _validate(self, value: int):
        if value==None:
            return False

        if not isnumeric(value) and not isinstance(value, bool):
            raise ValueError(f"{self._name} {value} is not a bool value!")

        if value==0 or value=='0' or value=='F' or value==False:
            return False
        else:
            return True

class DateTimeField(Field):
    def _validate(self, value):
        
        result=datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return result.isoformat()

    def _format_value(self, value, format):
        return datetime.fromisoformat(value).strftime(format)
        #return datetime.strftime(value, format)
