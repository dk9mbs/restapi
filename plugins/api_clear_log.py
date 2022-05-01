import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    xml=f"""
    <restapi type="delete">
        <table name="api_process_log"/>
        <filter type="AND">
            <condition field="status_id" value="10"/>
            <condition field="created_on" operator="olderThenXHours" value="1"/>
        </filter>
    </restapi>
    """
    fetch=FetchXmlParser(xml,context)
    DatabaseServices.exec(fetch,context)

