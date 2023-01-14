import chardet
from core import log

logger=log.create_logger(__name__)

def get_file_encoding(file, default_encoding='UTF-8'):
    encoding=default_encoding
    with open(file, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(100000))
        encoding=result['encoding']
        logger.info(f"detected encoding: {encoding} file:{file}")

    return encoding


def get_rawdata_encoding(raw_data, default_encoding='UTF-8'):
    encoding=default_encoding
    result = chardet.detect(raw_data)
    encoding=result['encoding']
    logger.info(f"detected encoding: {encoding}")

    return encoding
