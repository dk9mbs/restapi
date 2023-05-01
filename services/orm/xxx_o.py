class O:
    def __init__(self, field_name: str, order: str = "DESC") -> None:
        self._field_name=field_name
        self._order=order
        self._alias="main"

    @property
    def alias(self) -> str:
        return self._alias
    
    @alias.setter
    def alias(self, alias: str) -> str:
        self._alias=alias

    @property
    def field_name(self) -> str:
        return f"{self._alias}.{self._field_name}"
    
    @property
    def order(self) -> str:
        return self._order