"""
* ASGI Config

* For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
# Local Imports
import os

# Third Party Imports
from django.core.asgi import get_asgi_application

# Configure settings module and return ASGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
application = get_asgi_application()
