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


import asyncio
import atexit
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, NoReturn

import cv2
import numpy as np
from gpio import EdgeType, detect_edge
from remote.models import AlarmType, CameraParamsResponse, ProcessImageResponse
from remote.requests import get_camera_params, process_image, send_alarm
from utils.config import CAMERA_SENSOR_PIN, my_logger
from utils.models import AsyncList


class CameraReadError(Exception):
    pass


class CameraManager:
    def __init__(
        self,
        device: str
    ) -> None:
        atexit.register(self.cleanup)
        self.device: str = device
        my_logger.debug(f'Camera "{self.device}" configured.')

    @contextmanager
    def get_video_capture(self) -> Generator[cv2.VideoCapture, Any, None]:
        try:
            self._cap: cv2.VideoCapture = cv2.VideoCapture(self.device)
        except Exception as e:
            msg: str = f'Can\'t connect to the camera. {e}'
            asyncio.create_task(
                send_alarm(
                    alarm_type= AlarmType.CRITICAL,
                    message= msg
                )
            )
            my_logger.error(f'ConnectionError: {msg}.')
            raise ConnectionError(msg)
        try:
            if not self._cap.isOpened():
                msg: str = 'Can\'t connect to the camera. VideoCapture is not open.'
                asyncio.create_task(
                    send_alarm(
                        alarm_type= AlarmType.CRITICAL,
                        message= msg
                    )
                )
                my_logger.error(f'ConnectionError: {msg}')
                raise ConnectionError(msg)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            yield self._cap
        finally:
            self._cap.release()

    def cleanup(self) -> None:
        if self._cap is not None:
            self._cap.release()
            my_logger.info(f'Camera "{self.device}" cleared.')

    async def load_camera_props(self, cap: cv2.VideoCapture) -> None:
        props: CameraParamsResponse = await get_camera_params()
        self.set_width(cap, props.camera_width)
        self.set_height(cap, props.camera_height)
        self.set_brightness(cap, props.brightness)
        self.set_contrast(cap, props.contrast)
        self.set_saturation(cap, props.saturation)
        self.set_exposure(cap, props.exposure)
        self.set_auto_exposure(cap, props.auto_exposure)
        self.set_wb(cap, props.wb)
        self.set_auto_wb(cap, props.auto_wb)
        my_logger.debug(f'Loaded properties for "{self.device}": {props}.')

    def set_width(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, value)

    def set_height(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, value)

    def set_brightness(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_contrast(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_CONTRAST, value)

    def set_saturation(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_SATURATION, value)

    def set_exposure(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_EXPOSURE, value)

    def set_auto_exposure(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, value)

    def set_wb(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, value)

    def set_auto_wb(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_AUTO_WB, value)

    def capture_image(self, cap: cv2.VideoCapture) -> np.ndarray:
        ret: bool
        image: np.ndarray
        for _ in range(2):
            if not cap.grab():
                msg: str = 'Can\'t grab frame.'
                asyncio.create_task(
                    send_alarm(
                        alarm_type= AlarmType.CRITICAL,
                        message= msg
                    )
                )
                my_logger.error(f'CameraReadError: {msg}')
                raise CameraReadError(msg)
        ret, image = cap.retrieve()
        if not ret:
            msg: str = 'Can\'t retrieve frame.'
            asyncio.create_task(
                send_alarm(
                    alarm_type= AlarmType.CRITICAL,
                    message= msg
                )
            )
            my_logger.error(f'CameraReadError: {msg}')
            raise CameraReadError(msg)
        return image

    async def loop(
        self,
        cap: cv2.VideoCapture,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> NoReturn:
        last_sensor_val: bool = False
        edge_type: EdgeType = EdgeType.NONE
        while True:
            await asyncio.sleep(0.001)
            edge_type, last_sensor_val = await detect_edge(
                    pin= CAMERA_SENSOR_PIN,
                    last_value= last_sensor_val
                )
            if edge_type == EdgeType.RISING:
                date: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
                my_logger.info('Capturing new image...')
                image: np.ndarray = self.capture_image(cap)
                result: ProcessImageResponse = await process_image(
                    image= image,
                    date= date
                )
                await results_queue.put(result)
                my_logger.debug(f'Image captured with {result}.')

    async def cycle(
        self,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> NoReturn:
        try:
            while True:
                try:
                    with self.get_video_capture() as cap:
                        await self.load_camera_props(cap)
                        my_logger.info(f'"{self.device}" cycle started.')
                        await self.loop(cap= cap, results_queue= results_queue)
                except ConnectionError as e:
                    msg: str = f'"{self.device}" ConnectionError. {e}'
                    asyncio.create_task(
                        send_alarm(
                            alarm_type= AlarmType.CRITICAL,
                            message= msg
                        )
                    )
                    my_logger.error(msg)
                    await asyncio.sleep(0.5)
                    my_logger.info(f'Trying to reconnect "{self.device}".')
                except CameraReadError as e:
                    msg: str = f'"{self.device}" loop error. {e}'
                    asyncio.create_task(
                        send_alarm(
                            alarm_type= AlarmType.CRITICAL,
                            message= msg
                        )
                    )
                    my_logger.error(msg)
                    await asyncio.sleep(0.5)
                    my_logger.info(f'Trying to reconnect "{self.device}".')
        except asyncio.CancelledError:
            my_logger.info('Camera cycle cancelled.')
            raise
