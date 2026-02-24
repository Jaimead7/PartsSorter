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

from ...dependencies.config import API_URL, my_logger
from ...models.api import RequestOptions
from . import api_request


async def api_get_alarms_types() -> list[str]:
    options: RequestOptions = RequestOptions(
        url= f'{API_URL}/alarm/types/',
        headers= {
            'accept': 'application/json'
        },
        timeout= httpx.Timeout(timeout= 5.0)
    )
    response: Optional[httpx.Response] = await api_request(options)
    if response is None:
        return []
    try:
        return [alarm_type for alarm_type in response.json()]
    except Exception as e:
        my_logger.error(f'Error processing alarm types from the api. {e}')
        return []
