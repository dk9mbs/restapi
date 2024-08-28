from services.orm import *
from shared.model import *
from core.context import Context

class ActivityTools:
    def __init__(self):
        pass


    def create_alert_if_not_exists(self, context: Context,subject: str, tag: str, status_id: int):
        activity=api_activity.objects(context).select().where(api_activity.tag==tag).to_entity()
        if activity==None:
            activity=api_activity()
            activity.tag.value=tag
            activity.status_id.value=status_id
            activity.subject.value=subject
            activity.insert(context)
            print(activity.id.value)

        