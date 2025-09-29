import uvicorn
from quart import Quart, render_template

from .blueprints.config import config_bp

app = Quart(__name__)

@app.route('/')
@app.route('/index')
async def home() -> str:
    return await render_template('home.html')

@app.route('/image-stream')
async def image_stream() -> str:
    return await render_template('image-stream.html')

app.register_blueprint(config_bp)

if __name__ == '__main__':
    uvicorn.run(
        'app.app:app', #TODO: change to app
        host = 'localhost',
        port = 5000,
        reload= True #DELETE
    )
