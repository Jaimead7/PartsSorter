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
from datetime import datetime, timedelta, timezone
from typing import Optional

import cv2
import numpy as np
from gpio.gpio import GPIO
from pyUtils import Styles
from utils.config import (ACTUATOR_SENSOR_PIN, CAMERA, CAMERA_SENSOR_PIN,
                          MY_CFG, my_logger)
from utils.data_types import Result
from yoloModelManager import (CameraManager, ImageProcessing, ModelManager,
                              MyResults, camera_manager_factory)
from yoloModelManager.src.model.results import Box


def request_result(frame: np.ndarray):
    ... #TODO
    return False

def procces_local(camera: CameraManager, model: ModelManager) -> bool:
    PUSH_CLASSES: tuple = (
        0,
        1,
        4,
        5,
        8,
        9
    )
    model.process_frame(camera.last_frame)
    model_result: MyResults = model.result_tracker.results_hist[-1]
    cv2.imshow('Test', model.result_tracker.plot())
    cv2.waitKey(1)
    if model_result.valid_boxes is None:
        camera.save_last_frame(subfolder= 'Empty')
        my_logger.debug('Empty image.', Styles.CYAN)
        return False
    best_result: Box = model_result.valid_boxes.boxes[0]
    for box in model_result.valid_boxes.boxes:
        if box.conf > best_result.conf:
            best_result = box
    camera.save_last_frame(subfolder= model.object_classes[best_result.object_n])
    my_logger.debug(f'{model.object_classes[best_result.object_n]} detected ({best_result.object_n in PUSH_CLASSES}).', Styles.GREEN)
    return best_result.object_n in PUSH_CLASSES

async def camera_cycle(results_queue: asyncio.Queue[Result]) -> None:
    if CAMERA_SENSOR_PIN is None:
        msg: str = 'No pin is selected as "CAMERA_SENSOR_PIN".'
        my_logger.critical(msg)
        exit(1)
    try:
        camera: CameraManager = camera_manager_factory(CAMERA)
    except Exception as e:
        msg: str = f'Error on setting camera: {e}.'
        my_logger.critical(msg)
        exit(1)
    camera.save_filters = [ImageProcessing.FILTERS['RESIZE']] #DELETE: if frame is process in the cloud
    last_sensor_val: bool = False
    with camera.get_video_capture() as cap:
        camera.set_brightness(cap, MY_CFG.camera.brightness)
        camera.set_contrast(cap, MY_CFG.camera.contrast)
        camera.set_saturation(cap, MY_CFG.camera.saturation)
        camera.set_auto_exposure(cap, MY_CFG.camera.auto_exposure)
        camera.set_exposure(cap, MY_CFG.camera.exposure)
        camera.set_auto_wb(cap, MY_CFG.camera.auto_wb)
        camera.set_wb(cap, MY_CFG.camera.wb)
        model: ModelManager = ModelManager(MY_CFG.model.name) #DELETE
        cv2.namedWindow('Test', cv2.WINDOW_AUTOSIZE) #DELETE
        _time: datetime = datetime.now(timezone.utc)
        while True:
            await asyncio.sleep(0.001)
            #camera.capture_frame(cap) #DELETE
            #procces_local(camera, model) #DELETE
            #await asyncio.sleep(2) #DELETE
                
            new_sensor_value: Optional[bool] = GPIO.read(CAMERA_SENSOR_PIN)
            if new_sensor_value is None:
                continue
            if new_sensor_value and not last_sensor_val:
                my_logger.debug(f'Taking new image.')
                try:
                    camera.capture_frame(cap)
                    date: datetime = datetime.now(timezone.utc)
                    result: bool = request_result(camera.last_frame)
                    result: bool = procces_local(camera, model) #DELETE
                    await results_queue.put(Result(date= date, result= result))
                    my_logger.debug(f'New result added to the queue.')
                except RuntimeError:
                    pass
            last_sensor_val = new_sensor_value
            
