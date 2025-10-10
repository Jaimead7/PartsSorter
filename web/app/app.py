import uvicorn
from quart import Quart, render_template

from .blueprints import api_bp, config_bp
from .dependencies.config import SERVER_PORT, SERVER_IP

app = Quart(__name__)

@app.route('/')
@app.route('/index')
async def home() -> str:
    return await render_template('home.html')

@app.route('/image-stream')
async def image_stream() -> str:
    return await render_template('image-stream.html')

app.register_blueprint(config_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host= SERVER_IP,
        port= SERVER_PORT
    )
