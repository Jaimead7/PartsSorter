import httpx
from quart import Blueprint, Response, jsonify

from ..dependencies.config import API_URL, my_logger

api_bp = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

@api_bp.route('/config')
async def api_config():
    try:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.post(
                url= f'http://{API_URL}/config/ip',
                headers= {
                    'accept': 'application/json'
                }
            )
        return Response(response.json(), 200)
    except httpx.ConnectError:
        msg: str = 'Could not connect to the API.'
        my_logger.error(f'ConnectionError: {msg}')
        return Response(
            {
                'error': {
                    'code': 'internal_error',
                    'message': msg
                }
            },
            500
        )
