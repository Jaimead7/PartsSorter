from typing import Optional

import cv2
import httpx
import numpy as np
from utils.config import API_IP, ORIGIN_NAME, my_logger

from .models import ActuatorParams, CameraParams


async def get_camera_params() -> CameraParams:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url= f'http://{API_IP}/origin/{ORIGIN_NAME}/camera-params'
        )
    if response.status_code // 100 != 2:
        msg: str = f'Could not obtain the camera parameters from "{API_IP}". {response}.'
        my_logger.error(msg)
        raise RuntimeError(msg)
    return CameraParams(response.json())

async def get_origin_actuator_params() -> ActuatorParams:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url= f'http://{API_IP}/origin/{ORIGIN_NAME}/params'
        )
    if response.status_code // 100 != 2:
        msg: str = f'Could not obtain the parameters from "{API_IP}". {response}.'
        my_logger.error(msg)
        raise RuntimeError(msg)
    return ActuatorParams(response.json())

async def process_image(image: Optional[np.ndarray]) -> bool:
    if image is None:
        return False
    img_bytes: bytes = cv2.imencode('.png', image)[1].tobytes()
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(
            url= f'http://{API_IP}/image/process',
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
    return bool(response.json()['result'])
