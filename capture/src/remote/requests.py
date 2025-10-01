from typing import Optional

import cv2
import httpx
import numpy as np
from utils.config import API_IP, ORIGIN_NAME, my_logger

from .models import CameraProps


async def get_camera_props() -> CameraProps:
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.get(
            url= f'http://{API_IP}/origin/{ORIGIN_NAME}/camera-prop'
        )
    if response.status_code // 100 != 2:
        msg: str = f'Could not obtain the camera properties of "{API_IP}". {response.status_code}.'
        my_logger.error(msg)
        raise RuntimeError(msg)
    return CameraProps(response.json())

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
            params= {
                'origin': ORIGIN_NAME
            },
            files= {
                'file': ('image.png', img_bytes, 'image/png')
            }
        )
    return bool(response.json()['result'])
