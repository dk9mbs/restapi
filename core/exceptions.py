class RestApiNotAllowed(Exception):
    pass

class ConfigNotValid(Exception):
    pass

class DataViewNotFound(Exception):
    pass

class TableMetaDataNotFound(Exception):
    pass

class TableAliasNotFoundInFetchXml(Exception):
    pass

class FieldNotFoundInMetaData(Exception):
    pass

class MissingFieldPermisson(Exception):
    pass
