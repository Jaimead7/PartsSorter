import uvicorn
from quart import Quart, render_template

from .blueprints import api_bp, inspection_bp, wn_bp
from .dependencies.config import SERVER_IP, SERVER_PORT

app = Quart(__name__)

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
        'app.app:app',
        host= SERVER_IP,
        port= SERVER_PORT,
        reload= True,
        reload_dirs=['.', './templates', './static'],
        reload_includes=['*.py', '*.html', '*.css', '*.js']
    )
