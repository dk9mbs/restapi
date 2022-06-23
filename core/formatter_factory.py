import importlib

from core import log
from core.appinfo import AppInfo
from core import log

logger=log.create_logger(__name__)

class FormatterFactory:

    def __init__(self, context, formatter_name):
        self._formatter_name=formatter_name
        self._context=context

    def create(self):
        mod=None
        try:
            mod=importlib.import_module(self._formatter_name)
        except ImportError as err:
            logger.exception(err)

        return mod
