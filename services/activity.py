import datetime

from services.orm import *
from shared.model import *
from core.context import Context

class Activity:
    def __init__(self, context: Context) -> any:
        self._context=context


    def create_alert_if_not_exists(self, subject: str, msg_text: str, tag: str, status_id: int):
        activity=api_activity.objects(self._context).select().where(api_activity.tag==tag) \
            .where(api_activity.status_id==status_id).to_entity()
            
        result=0
        if activity==None:
            activity=api_activity()
            activity.tag.value=tag
            activity.status_id.value=status_id
            activity.subject.value=subject
            activity.msg_text.value=msg_text
            activity.type_id.value=4
            activity.due_date.value=datetime.datetime.now()
            result=activity.insert(self._context)
        else:
            activity.msg_text.value=activity.msg_text.value+msg_text
            #activity.update(self._context)
            result=activity.id.value
        
        return result
    
