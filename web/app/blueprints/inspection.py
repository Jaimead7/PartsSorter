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
from quart import Blueprint, redirect, render_template, request
from werkzeug import Response

from ..dependencies.api import (api_get_image_extensions,
                                api_get_inspection_results, api_get_models,
                                api_get_origins)
from ..models.api import (InspectionResultResponse, ModelResponse,
                          OriginResponse)

inspection_bp = Blueprint(
    'inspection',
    __name__,
    url_prefix='/inspection'
)

@inspection_bp.route('/image-stream/')
async def image_stream() -> str:
    try:
        origins: list[OriginResponse] = await api_get_origins()
    except httpx.ConnectError:
        origins = []
    preselected_origins: list[str] = request.args.getlist('origin')
    return await render_template(
        'image-stream.html',
        page_title= 'Image stream',
        origins= origins,
        preselected_origins= preselected_origins
    )

@inspection_bp.route('/image-inspection/')
async def image_inspection() -> Response | str:
    try:
        origins: list[OriginResponse] = await api_get_origins()
        models: list[ModelResponse] = await api_get_models()
        classes: list[InspectionResultResponse] = await api_get_inspection_results()
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
