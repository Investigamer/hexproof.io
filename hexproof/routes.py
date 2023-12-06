"""
* API Endpoint Routes
"""
# Third Party Imports
from django.urls import path
from ninja import NinjaAPI

# Local Imports
from hexproof.endpoints.keys import api as route_keys
from hexproof.endpoints.mtg.sets import api as route_sets
from hexproof.endpoints.mtg.symbols import api as route_symbols

# Add our API endpoints
api = NinjaAPI(
    docs_url='docs/',
    title='Hexproof API')
api.add_router('key/', route_keys)
api.add_router('sets/', route_sets)
api.add_router('symbols/', route_symbols)

# Route the root URL to the API
urlpatterns = [
    path('', api.urls)
]
