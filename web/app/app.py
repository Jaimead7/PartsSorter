import uvicorn
from quart import Quart, render_template, render_template_string

from .blueprints import api_bp, config_bp
from .dependencies.config import SERVER_IP, SERVER_PORT

app = Quart(__name__)

@app.route('/')
@app.route('/index')
async def home() -> str:
    return await render_template(
        'index.html',
        page_title= 'PART INSPECTION'
    )

@app.route('/image-stream')
async def image_stream() -> str:
    return await render_template(
        'image-stream.html',
        page_title= 'Airbag cut inspection - Image stream'
    )

app.register_blueprint(config_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    uvicorn.run(
        'app.app:app',
        host= SERVER_IP,
        port= SERVER_PORT,
        reload= True,
        reload_dirs=['.', './templates', './static'],
        reload_includes=['*.py', '*.html', '*.css', '*.js']
    )
