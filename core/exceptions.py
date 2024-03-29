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

class FileNotFoundInDatabase(Exception):
    pass

class UnknownMimeType(Exception):
    pass

class FetchXmlFormat(Exception):
    pass

class SpecialCharsInFetchXml(Exception):
    pass

class MissingArgumentInFetchXml(Exception):
    pass

class OperatorNotAllowedInFetchXml(Exception):
    pass

class OutDataFormatterNotFound(Exception):
    pass

class TypeNotAllowedInFieldList(Exception):
    pass

class WrongFetchMode(Exception):
    pass

class NotAllowedDataClass(Exception):
    pass