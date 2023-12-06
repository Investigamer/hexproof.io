"""
* WSGI Config

* For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
# Local Imports
import os

# Third Party Imports
from django.core.wsgi import get_wsgi_application

# Configure settings module and return WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
application = get_wsgi_application()
