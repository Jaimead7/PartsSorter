# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmial.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import asyncio
import atexit
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, NoReturn, Optional

import cv2
import numpy as np
from gpio import GPIO
from remote.models import CameraProps
from remote.requests import get_camera_props, process_image
from utils.config import CAMERA_SENSOR_PIN, my_logger
from utils.data_types import Result


class CameraManager:
    def __init__(
        self,
        index: int
    ) -> None:
        atexit.register(self.cleanup)
        self.index = index

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:
        self._index: int = value
        with self.get_video_capture() as _:
            pass

    @contextmanager
    def get_video_capture(self) -> Generator[cv2.VideoCapture, Any, None]:
        self._cap: cv2.VideoCapture = cv2.VideoCapture(self.index)
        if not self._cap.isOpened():
            msg: str = 'Can\'t connect to the camera.'
            my_logger.error(f'ConnectionRefusedError: {msg}')
            raise ConnectionRefusedError(msg)
        try:
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            yield self._cap
        finally:
            self._cap.release()

    def cleanup(self) -> None:
        if self._cap is not None:
            self._cap.release()
            my_logger.debug(f'Camera {self.index} cleared.')

    async def load_camera_props(self, cap: cv2.VideoCapture) -> None:
        props: CameraProps = await get_camera_props()
        self.set_width(cap, props['camera_width'])
        self.set_height(cap, props['camera_height'])
        self.set_brightness(cap, props['brightness'])
        self.set_contrast(cap, props['contrast'])
        self.set_saturation(cap, props['saturation'])
        self.set_exposure(cap, props['exposure'])
        self.set_wb(cap, props['wb'])

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

    def set_wb(self, cap: cv2.VideoCapture, value: int) -> None:
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, value)

    def capture_image(self, cap: cv2.VideoCapture) -> Optional[np.ndarray]:
        ret: bool
        image: np.ndarray
        for _ in range(2):
            cap.grab()
        ret, image = cap.retrieve()
        if not ret:
            msg: str = 'Can\'t read frame.'
            my_logger.error(f'{msg}')
            return None
        return image

    async def cycle(self, results_queue: asyncio.Queue[Result]) -> NoReturn:
        last_sensor_val: bool = False
        with self.get_video_capture() as cap:
            await self.load_camera_props(cap)
            while True:
                await asyncio.sleep(0.001)
                new_sensor_value: Optional[bool] = GPIO.read(CAMERA_SENSOR_PIN)
                if new_sensor_value is None:
                    continue
                if new_sensor_value and not last_sensor_val:
                    my_logger.debug('Capturing new image.')
                    date: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
                    result: bool = await process_image(self.capture_image(cap))
                    await results_queue.put(
                        Result(
                            date= date,
                            result= result
                        )
                    )
