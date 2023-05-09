from services.orm.base_manager import BaseManager
from services.orm.field import Field

class MetaModel(type):
    manager_class = BaseManager

    def __new__(cls, name, bases, dct):
        result=type.__new__(cls, name, bases, dct)

        if dct['__qualname__']!="BaseModel":
            for key, value in dct.items():
                if isinstance(value, Field):
                    value.clear()
                    value.bind(result, key)
        return result

    def _get_manager(cls):
        return cls.manager_class(model_class=cls)


    @property
    def objects(cls):
        return cls._get_manager()





class BaseModel(metaclass=MetaModel):
    def __init__(self, **row_data):
        """
        Reset alle Field attributes
        """
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field):
                object.__getattribute__(self, key).clear()

        """
        Import the values from the method argument
        """
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

    def insert(self) -> bool:
        data=dict()
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field) and value.dirty:
                data[key]=value.value

        BaseModel.manager_class(model_class=self.__class__).insert(data)

        return True

    def update(self) -> bool:
        data=dict()
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field) and value.dirty:
                data[key]=value.value

        BaseModel.manager_class(model_class=self.__class__).update(data)

        return True

    class Meta:
        table_name=""
        table_alias=""