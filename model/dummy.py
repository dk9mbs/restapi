from services.orm import BaseModel, NumericField, StringField, IntField

class Dummy(BaseModel):
    table_name="dummy"

    """
    Field Definition
    """
    id=IntField(pk=True)
    name=StringField()
    Port=IntField()

    class Meta:
        table_name="dummy"
        table_alias="dummy"