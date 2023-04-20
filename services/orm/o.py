class O:
    def __init__(self, field_name: str, order: str) -> None:
        self._field_name=field_name
        self._order=order

    def get_field_name(self) -> str:
        return self._field_name
    
    def get_order(self) -> str:
        return self._order