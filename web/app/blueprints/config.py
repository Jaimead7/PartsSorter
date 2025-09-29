from quart import Blueprint, render_template

config_bp = Blueprint(
    'config',
    __name__,
    url_prefix='/config'
)

@config_bp.route('/models')
async def models() -> str:
    return await render_template('config/models.html')

@config_bp.route('/origins')
async def origins() -> str:
    return await render_template('config/origins.html')

@config_bp.route('/inspection-results')
async def inspection_results() -> str:
    return await render_template('config/inspection-results.html')

@config_bp.route('/model-classes')
async def model_classes() -> str:
    return await render_template('config/model-classes.html')

@config_bp.route('/images')
async def images() -> str:
    return await render_template('config/images.html')
