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


from typing import Optional

import httpx
from quart import Blueprint, redirect, render_template
from werkzeug import Response

from ...dependencies.api import api_get_models, api_get_origin, api_get_origins
from ...models.api import ModelResponse, OriginResponse

origin_config_bp = Blueprint(
    'config-origins',
    __name__,
    url_prefix='/origins'
)

@origin_config_bp.route('/')
async def config_origins() -> Response | str:
    try:
        origins: list[OriginResponse] = await api_get_origins()
    except httpx.ConnectError:
        return redirect('/config', 302)
    return await render_template(
        'config/origin/origins-list.html',
        page_title= 'Configuration',
        origins= origins
    )

@origin_config_bp.route('/add/')
async def add_origin() -> Response | str:
    models: list[ModelResponse] = []
    try:
        models += await api_get_models()
    except httpx.ConnectError:
        pass
    return await render_template(
        'config/origin/origin-add.html',
        page_title= 'Configuration',
        models= models
    )

@origin_config_bp.route(f'/<path:origin_name>/')
async def config_origin(origin_name: str) -> Response | str:
    try:
        origin: Optional[OriginResponse] = await api_get_origin(origin_name)
        origins: list[OriginResponse] = await api_get_origins()
    except httpx.ConnectError:
        return redirect('/config/origins/', 302)
    if origin is None:
        return redirect('/config/origins/', 302)
    models: list[ModelResponse] = []
    try:
        models += await api_get_models()
    except httpx.ConnectError:
        pass
    return await render_template(
        'config/origin/origin.html',
        page_title= 'Configuration',
        origin= origin,
        origins= origins,
        models= models
    )
