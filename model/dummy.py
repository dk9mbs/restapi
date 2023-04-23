from services.orm import BaseModel, NumericField, StringField

class Dummy(BaseModel):
    table_name="dummy"

    """
    Field Definition
    """
    id=NumericField('id', None)
    name=StringField('name', None)
    Port=NumericField('Port', None)

