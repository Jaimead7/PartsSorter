import httpx
import uvicorn
from quart import Quart, render_template

from .blueprints import api_bp, inspection_bp, wn_bp
from .dependencies.config import SERVER_IP, SERVER_PORT

app = Quart(__name__)

@app.before_serving
async def create_httpx_client() -> None:
    app.extensions['httpx_client'] = httpx.AsyncClient()

@app.after_serving
async def close_httpx_client() -> None:
    client: httpx.AsyncClient = app.extensions['httpx_client']
    await client.aclose()

@app.route('/')
@app.route('/index')
async def home() -> str:
    return await render_template(
        'index.html',
        page_title= 'Part inspection'
    )

app.register_blueprint(inspection_bp)
app.register_blueprint(api_bp)
app.register_blueprint(wn_bp)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host= SERVER_IP,
        port= SERVER_PORT
    )
