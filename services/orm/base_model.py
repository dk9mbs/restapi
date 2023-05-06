from core.context import Context
from services.orm.base_manager import BaseManager
from services.orm.field import Field

class MetaModel(type):
    manager_class = BaseManager

    def __new__(cls, name, bases, dct):
        result=type.__new__(cls, name, bases, dct)

        if dct['__qualname__']!="BaseModel":
            for key, value in dct.items():
                if isinstance(value, Field):
                    value.bind(result, key)
        return result

    def _get_manager(cls):
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        return cls._get_manager()




class BaseModel(metaclass=MetaModel):

    def __init__(self, **row_data):
        for field_name, value in row_data.items():
            f=getattr(self, field_name)
            f.value=value
            #setattr(self, field_name, f)
        
    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>"

    @classmethod
    def get_fields(cls):
        return cls._get_manager()._get_fields()

    class Meta:
        table_name=""
        table_alias=""