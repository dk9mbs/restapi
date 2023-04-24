from services.orm import BaseModel, NumericField, StringField, IntField

class Dummy(BaseModel):
    table_name="dummy"

    """
    Field Definition
    """
    id=IntField('id', pk=True)
    name=StringField('name')
    Port=NumericField('Port')

