from services.orm.base_manager import BaseManager
from services.orm.field import Field

class MetaModel(type):
    manager_class = BaseManager

    def _get_manager(cls, context):
        return cls.manager_class(context=context, model_class=cls)

    def get_objects(cls, context):
        return cls._get_manager(context)

class BaseModel(metaclass=MetaModel):
    table_name = ""

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
