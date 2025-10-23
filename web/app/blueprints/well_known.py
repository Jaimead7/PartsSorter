from quart import Blueprint, Response, jsonify

wn_bp = Blueprint(
    'well-known',
    __name__,
    url_prefix='/.well-known'
)

@wn_bp.route('/appspecific/com.chrome.devtools.json')
async def chrome_dev_tools() -> Response:
    config: dict = {}
    return jsonify(config)
