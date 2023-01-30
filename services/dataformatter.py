from services.jinjatemplate import JinjaTemplate

class DataFormatter(object):
    def __init__(self, context, data, template):
        self._context=context
        self._data=data
        self._template=template

    def render(self):
        template=JinjaTemplate.create_string_template(self._context,self._template)
        result = template.render(self._data )

        return result

