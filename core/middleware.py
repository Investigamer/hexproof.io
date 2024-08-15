"""
* Core Django Middleware

* Provides top-level middleware for requests to our Django app.
"""
# Standard Library Imports
from django.http import HttpResponseRedirect, HttpRequest
from django.utils.deprecation import MiddlewareMixin

# Local Imports
from core import settings

"""
* Middleware Classes
"""


class SubdomainRoutesMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request: HttpRequest):
        """Route request to the correct subdomain, falling back to base domain if no patterns match.

        Args:
            request: Request object.
        """

        # Check for a subdomain
        host_full = request.get_host()
        host = host_full.split('.')
        if len(host) < 3:
            return

        # Get subdomain and routes
        subdomain = host[0]
        subdomain_routes = getattr(settings, 'SUBDOMAIN_ROUTES', {})

        # Check for a specific subdomain route
        if subdomain in subdomain_routes:
            request.urlconf = subdomain_routes[subdomain]
        else:
            # Check for a default route
            if '*' in subdomain_routes:
                request.urlconf = subdomain_routes['*']
            else:
                # Redirect to the base domain
                return HttpResponseRedirect(
                    request.build_absolute_uri().replace(
                        host_full, '.'.join(host[1:])))
