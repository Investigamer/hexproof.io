"""
* API Endpoint Routes
"""
# Third Party Imports
from ninja import NinjaAPI

# Local Imports
from api.endpoints.keys import api as route_keys
from api.endpoints.meta import api as route_meta
from api.endpoints.mtg.sets import api as route_sets
from api.endpoints.mtg.symbols import api as route_symbols
from api.utils.renderer import PrettyJSON

# Add our API endpoints
APIRouter = NinjaAPI(
    docs_url='docs/',
    title='Hexproof API',
    renderer=PrettyJSON())
APIRouter.add_router('/keys/', route_keys)
APIRouter.add_router('/meta/', route_meta)
APIRouter.add_router('/sets/', route_sets)
APIRouter.add_router('/symbols/', route_symbols)
