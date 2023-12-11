"""
* API Endpoint Routes
"""
# Third Party Imports
from ninja import NinjaAPI

# Local Imports
from hexproof.endpoints.keys import api as route_keys
from hexproof.endpoints.meta import api as route_meta
from hexproof.endpoints.mtg.sets import api as route_sets
from hexproof.endpoints.mtg.symbols import api as route_symbols
from hexproof.schemas import PrettyJSON

# Add our API endpoints
api = NinjaAPI(
    docs_url='docs/',
    title='Hexproof API',
    renderer=PrettyJSON())
api.add_router('/keys/', route_keys)
api.add_router('/meta/', route_meta)
api.add_router('/sets/', route_sets)
api.add_router('/symbols/', route_symbols)
