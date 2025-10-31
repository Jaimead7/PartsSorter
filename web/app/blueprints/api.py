import httpx
from quart import Blueprint, Response

from ..dependencies.api import api_get_ip
from ..dependencies.config import my_logger

api_bp = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

@api_bp.route('/config')
async def api_config() -> Response:
    try:
        ip: str = await api_get_ip()
        return Response(
            ip,
            200,
            content_type='application/json'
        )
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
