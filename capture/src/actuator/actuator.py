# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
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

from gpio.gpio import GPIO
from utils.config import (ACTUATOR_PIN, ACTUATOR_SENSOR_PIN,
                          SENSORS_INTERVAL_MS, my_logger)
from utils.data_types import Result


async def actuator_cycle(results_queue: asyncio.Queue[Result]) -> None:
    last_sensor_val: bool = False
    new_result: Optional[Result] = None
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
                    if now - new_result['date'] < timedelta(milliseconds= SENSORS_INTERVAL_MS):
                        my_logger.debug(f'New part to push with Result{new_result}.')
                        break
                new_result = None
        if not new_sensor_value and last_sensor_val:
            my_logger.debug(f'Part to be pushed with Result{new_result}.')
            if new_result is not None:
                GPIO.write(ACTUATOR_PIN, new_result["result"])
                await asyncio.sleep(1)
                GPIO.write(ACTUATOR_PIN, False)
            new_result = None
        last_sensor_val = new_sensor_value
