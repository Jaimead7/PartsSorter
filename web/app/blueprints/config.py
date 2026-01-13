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

from ..dependencies.api import api_get_model, api_get_models
from ..models.api import ModelResponse

config_bp = Blueprint(
    'api',
    __name__,
    url_prefix='/config'
)

@config_bp.route('/')
async def config() -> str:
    return await render_template(
        'config/config-menu.html',
        page_title= 'Configuration'
    )

@config_bp.route('/models')
async def config_models() -> Response | str:
    try:
        models: list[ModelResponse] = await api_get_models()
    except httpx.ConnectError:
        return redirect('/config', 302)
    return await render_template(
        'config/models-list.html',
        page_title= 'Configuration',
        models= models
    )

@config_bp.route('/models/load')
async def load_model() -> Response | str:
    return await render_template(
        'config/model-load.html',
        page_title= 'Configuration'
    )

@config_bp.route(f'/models/<path:model_name>')
async def config_model(model_name: str) -> Response | str:
    try:
        model: Optional[ModelResponse] = await api_get_model(model_name)
        models: list[ModelResponse] = await api_get_models()
    except httpx.ConnectError:
        return redirect('/config/models', 302)
    if model is None:
        return redirect('/config/models', 302)
    return await render_template(
        'config/model.html',
        page_title= 'Configuration',
        model= model,
        models= models
    )
