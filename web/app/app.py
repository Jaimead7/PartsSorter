# MIT License

# Copyright (c) 2025 Jaime Álvarez Díaz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import httpx
import uvicorn
from quart import Quart, render_template

from .blueprints import config_bp, inspection_bp, wk_bp
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

@app.get('/health')
async def health_check() -> dict:
    return {"status": "healthy", "service": "web"}

app.register_blueprint(inspection_bp)
app.register_blueprint(config_bp)
app.register_blueprint(wk_bp)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host= SERVER_IP,
        port= SERVER_PORT
    )
