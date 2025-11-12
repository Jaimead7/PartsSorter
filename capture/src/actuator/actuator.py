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

from gpio.gpio import GPIO, CheckEdgeRespone
from remote.models import ActuatorParamsResponse, ProcessImageResponse
from remote.requests import get_actuator_params
from utils.config import ACTUATOR_PIN, ACTUATOR_SENSOR_PIN, my_logger
from utils.models import AsyncList


class ActuatorManager:
    def __init__(
        self
    ) -> None:
        self.last_sensor_val: bool = False
        self.params: Optional[ActuatorParamsResponse] = None
        self.next_part_to_push: ProcessImageResponse = ProcessImageResponse(
            result= False
        )
        self.last_push: datetime = datetime.now(timezone.utc).replace(tzinfo=None)

    @property
    def sensors_interval_ms(self) -> float:
        if self.params is None:
            msg: str = 'Params not loaded. Call await load_params() first.'
            my_logger.critical(msg)
            raise RuntimeError(msg)
        return (self.params.sensors_distance / self.params.tape_speed) * 1000

    async def load_params(self) -> None:
        self.params = await get_actuator_params()

    async def push(self) -> None:
        if self.params is None:
            msg: str = 'Params not loaded. Call await load_params() first.'
            my_logger.critical(msg)
            raise RuntimeError(msg)
        await asyncio.sleep(self.params.actuator_delay / 1000.)
        now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        if self.last_push - now > timedelta(milliseconds= self.params.actuator_cycle_time):
            #FIXME: what happens if de delay is to long and a new part reach the actuator. self.next_part_to_push will be modified.
            my_logger.debug(f'Pushing new part with Result({self.next_part_to_push}).')
            self.last_push = now
            GPIO.write(ACTUATOR_PIN, True)
            await asyncio.sleep(0.2)
            GPIO.write(ACTUATOR_PIN, False)
        else:
            my_logger.error(f'Part skiped with Result({self.next_part_to_push}). Tried to push so early.')

    async def get_next_result(
        self,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> None:
        now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        while True:
            try:
                next_result: ProcessImageResponse = await results_queue.check_first()
            except asyncio.QueueEmpty:
                my_logger.error('Result lost. There are no results in the queue. The part will be pushed.')
                self.next_part_to_push = ProcessImageResponse(
                    date= now,
                    result= True
                )
                break
            if now - next_result.date < timedelta(milliseconds= self.sensors_interval_ms * 0.8):
                my_logger.error('Result lost. The part doesn\'t have a result on the queue. The part will be pushed.')
                self.next_part_to_push = ProcessImageResponse(
                    date= now,
                    result= True
                )
                break
            if now - next_result.date > timedelta(milliseconds= self.sensors_interval_ms * 1.2):
                my_logger.error('Part lost. The part of this result didn\'t reach the actuator.')
                await results_queue.get()
                continue
            self.next_part_to_push = await results_queue.get()
            my_logger.debug(f'New part on the actuator with Result({self.next_part_to_push}).')
            break

    async def cycle(
        self,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> NoReturn:
        if self.params is None:
            await self.load_params()
        try:
            my_logger.info(f'Actuator cycle started.')
            while True:
                await asyncio.sleep(0.001)
                rise_edge_response: CheckEdgeRespone = GPIO.check_rise_edge(
                    ACTUATOR_SENSOR_PIN,
                    self.last_sensor_val
                )
                fall_edge_response: CheckEdgeRespone = GPIO.check_fall_edge(
                    ACTUATOR_SENSOR_PIN,
                    self.last_sensor_val
                )
                self.last_sensor_val = fall_edge_response.new_value
                if rise_edge_response.result:
                    my_logger.debug(f'New part on the actuator.')
                    await self.get_next_result(results_queue)
                if fall_edge_response.result:
                    my_logger.debug(f'Part to be pushed with Result({self.next_part_to_push}).')
                    if self.next_part_to_push.result:
                        asyncio.create_task(self.push())
                    self.next_part_to_push = ProcessImageResponse(result= False)
        except asyncio.CancelledError:
            my_logger.info('Actuator cycle cancelled.')
            raise
