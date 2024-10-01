"""
* API Endpoint Routes
"""
# Third Party Imports
from ninja import NinjaAPI

# Local Imports
from api.endpoints.keys import router as router_keys
from api.endpoints.meta import router as router_meta
from api.endpoints.sets import router as router_sets
from api.endpoints.symbols import router as router_symbols
from api.utils.renderer import PrettyJSON

# Add our API endpoints
main_router = NinjaAPI(
    docs_url='/docs/',
    title='Hexproof API',
    renderer=PrettyJSON())
main_router.add_router('/keys/', router_keys)
main_router.add_router('/meta/', router_meta)
main_router.add_router('/sets/', router_sets)
main_router.add_router('/symbols/', router_symbols)
