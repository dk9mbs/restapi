import datetime
import requests

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    xml=f"""
    <restapi type="delete">
        <table name="api_session"/>
        <filter type="AND">
            <condition field="last_access_on" operator="olderThenXHours" value="48"/>
        </filter>
    </restapi>
    """
    fetch=FetchXmlParser(xml,context)
    DatabaseServices.exec(fetch,context,run_as_system=True)

