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


from datetime import datetime
from typing import Optional

import cv2
import httpx
import numpy as np
from pydantic import ValidationError
from utils.config import API_URL, ORIGIN_NAME, my_logger

from .models import (ActuatorParamsResponse, CameraParamsResponse,
                     ProcessImageResponse)


async def get_origin_params() -> httpx.Response:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url= f'{API_URL}/origin/{ORIGIN_NAME}/params/',
            headers= {
                'accept': 'application/json'
            }
        )
    if response.status_code // 100 != 2:
        msg: str = f'Could not obtain the origin parameters from "{API_URL}". {response}.'
        my_logger.error(msg)
        raise RuntimeError(msg)
    return response

async def get_camera_params() -> CameraParamsResponse:
    response: httpx.Response = await get_origin_params()
    try:
        return CameraParamsResponse(**response.json())
    except ValidationError:
        msg: str = f'Error during validation of camera parameters from "{API_URL}". {response.json()}.'
        my_logger.error(msg)
        raise RuntimeError(msg)

async def get_actuator_params() -> ActuatorParamsResponse:
    response: httpx.Response = await get_origin_params()
    try:
        return ActuatorParamsResponse(**response.json())
    except ValidationError:
        msg: str = f'Error during validation of actuator parameters from "{API_URL}". {response.json()}.'
        my_logger.error(msg)
        raise RuntimeError(msg)

async def process_image(
    image: Optional[np.ndarray],
    date: datetime
) -> ProcessImageResponse:
    if image is None:
        return ProcessImageResponse(
            date= date
        )
    img_bytes: bytes = cv2.imencode('.png', image)[1].tobytes()
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(
            url= f'{API_URL}/image/process/',
            headers= {
                'accept': 'application/json'
            },
            data= {
                'origin': ORIGIN_NAME
            },
            files= {
                'file': ('image.png', img_bytes, 'image/png')
            },
            timeout= httpx.Timeout(timeout= 10.0)
        )
        my_logger.debug(f'Response from server: {response}')
    response_json: dict = response.json()
    return ProcessImageResponse(
        date= date,
        id= response_json['id'],
        result= response_json['result']
    )
