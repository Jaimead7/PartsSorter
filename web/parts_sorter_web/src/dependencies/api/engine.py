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
from quart import current_app

from ...dependencies.config import my_logger
from ...models.api import RequestOptions


async def api_request(options: RequestOptions, method: str = 'GET') -> Optional[httpx.Response]:
    url_for_log: str = options.get('url', 'unknown').split('?')[0]
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    if client is None:
        my_logger.error('HTTP client not available.')
        return None
    try:
        if method.upper() == 'POST':
            response: httpx.Response = await client.post(**options)
        elif method.upper() == 'PUT':
            response: httpx.Response = await client.put(**options)
        elif method.upper() == 'DELETE':
            response: httpx.Response = await client.delete(**options)
        else:
            response: httpx.Response = await client.get(**options)
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            my_logger.warning(f'Response from "{url_for_log}": Not found.')
            return None
        my_logger.error(f'HTTP error from "{url_for_log}: {e.response.status_code}.')
        return None
    except httpx.RequestError as e:
        my_logger.error(f'Request failed from "{url_for_log}": {e}.')
        return None
    except Exception as e:
        my_logger.error(f'Unexpected error from "{url_for_log}": {e}')
        return None
