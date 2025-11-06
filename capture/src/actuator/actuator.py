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
from datetime import datetime, timedelta, timezone
from typing import NoReturn, Optional

from gpio.gpio import GPIO
from remote.models import ActuatorParams
from remote.requests import get_actuator_params
from utils.config import ACTUATOR_PIN, ACTUATOR_SENSOR_PIN, my_logger
from utils.data_types import Result


async def push_in_t_ms(t: float) -> None:
    await asyncio.sleep(t)
    my_logger.debug(f'Pushing new part.')
    GPIO.write(ACTUATOR_PIN, True)
    await asyncio.sleep(0.2)
    GPIO.write(ACTUATOR_PIN, False)

async def actuator_cycle(results_queue: asyncio.Queue[Result]) -> NoReturn:
    try:
        last_sensor_val: bool = False
        new_result: Optional[Result] = None
        params: ActuatorParams = await get_actuator_params()
        SENSORS_INTERVAL_MS: float = (params.sensors_distance / params.tape_speed) * 1000
        my_logger.info(f'Actuator cycle started.')
        while True:
            await asyncio.sleep(0.001)
            new_sensor_value: Optional[bool] = GPIO.read(ACTUATOR_SENSOR_PIN)
            if new_sensor_value is None:
                continue
            if new_sensor_value and not last_sensor_val:
                my_logger.debug(f'New part on the actuator.')
                now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
                new_result = Result(
                    date= now,
                    result= False
                )
                while not results_queue.empty():
                    try:
                        new_result = results_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    if new_result is not None:
                        if now - new_result.date < timedelta(milliseconds= SENSORS_INTERVAL_MS):
                            my_logger.debug(f'New part to push with Result{new_result}.')
                            break
                    new_result = None
            if not new_sensor_value and last_sensor_val:
                my_logger.debug(f'Part to be pushed with Result{new_result}.')
                if new_result is not None and new_result.result:
                    asyncio.create_task(push_in_t_ms(params.actuator_delay))
                new_result = None
            last_sensor_val = new_sensor_value
    except asyncio.CancelledError:
        my_logger.info('Actuator cycle cancelled.')
        raise
