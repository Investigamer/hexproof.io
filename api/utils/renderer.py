"""
* Utils for Rendering HTTP Responses
"""
# Standard Library Imports
import json

# Third Party Imports
from django.http import HttpRequest
from omnitils.strings import str_to_bool_safe
from ninja.renderers import JSONRenderer

"""
* JSON Renderers
"""


class PrettyJSON(JSONRenderer):
    """Render JSON as 'Pretty' if requested."""
    media_type = "application/json"

    def render(self, request: HttpRequest, data, *, response_status):
        if str_to_bool_safe(request.GET.get('pretty', 'false')):  # noqa
            return json.dumps(data, cls=self.encoder_class, **{'indent': 2})
        return super().render(request, data, response_status=response_status)
