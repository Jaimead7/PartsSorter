import httpx
from quart import Blueprint, redirect, render_template, request
from werkzeug import Response

from ..dependencies.api import (api_get_image_extensions,
                                api_get_inspection_results, api_get_models,
                                api_get_origins)

inspection_bp = Blueprint(
    'inspection',
    __name__,
    url_prefix='/inspection'
)

@inspection_bp.route('/image-stream')
async def image_stream() -> str:
    try:
        origins: list[str] = await api_get_origins()
    except httpx.ConnectError:
        origins = []
    preselected_origins: list[str] = request.args.getlist('origin')
    return await render_template(
        'image-stream.html',
        page_title= 'Image stream',
        origins= origins,
        preselected_origins= preselected_origins
    )

@inspection_bp.route('/image-inspection')
async def image_inspection() -> Response | str:
    try:
        origins: list[str] = await api_get_origins()
        models: list[str] = await api_get_models()
        classes: list[str] = await api_get_inspection_results()
        image_extensions: list[str] = await api_get_image_extensions()
    except httpx.ConnectError:
        return redirect('/', 302)
    return await render_template(
        'image-inspection.html',
        page_title= 'Image inspection',
        origins= origins,
        models= models,
        classes= classes,
        image_extensions= image_extensions
    )
