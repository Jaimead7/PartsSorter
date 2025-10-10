from quart import Blueprint
import httpx

from ..dependencies.config import API_URL


api_bp = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

@api_bp.route('/config')
async def api_config() -> dict:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(
            url= f'http://{API_URL}/config/ip',
            headers= {
                'accept': 'application/json'
            }
        )
    return response.json()
