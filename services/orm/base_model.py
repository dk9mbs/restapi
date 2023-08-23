from core.context import Context
from services.orm.base_manager import BaseManager
from services.orm.field import Field
from services.orm.expression import Expression, WhereExpression

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

    def _get_manager(cls, context: object):
        return cls.manager_class(context, model_class=cls)

    def objects(cls, context: object):
        return cls._get_manager(context)

class BaseModel(metaclass=MetaModel):
    #def __init__(self, **row_data):
    def __init__(self, row_data: dict={}) -> None:
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
            #f.dirty=False

    def __repr__(self):
        attrs_format = ", ".join([f'{field}={value}' for field, value in self.__class__.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})>"

    @classmethod
    def get_fields(cls, context: object):
        return cls._get_manager()._get_fields()

    def insert(self, context: Context()) -> bool:
        data=dict()
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field) and value.dirty:
                data[key]=value.value

        BaseModel.manager_class(context ,model_class=self.__class__).insert(data)

        return True

    def update(self, context: Context) -> bool:
        data=dict()
        expression=WhereExpression()
        key_count=0

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field) and value.dirty:
                data[key]=value.value

            # for where clause use not the dirty flag
            if isinstance(value, Field):
                if value.primary_key:
                    expression=expression & WhereExpression(f"{value.table_alias}.{value.name}", "=", value.value)
                    key_count+=1

        if key_count==0:
            raise Exception(f"No primary key in model defined for table {self.Meta.table_name}")

        BaseModel.manager_class(context, model_class=self.__class__).update(expression, data)

        return True

    class Meta:
        table_name=""
        table_alias=""
