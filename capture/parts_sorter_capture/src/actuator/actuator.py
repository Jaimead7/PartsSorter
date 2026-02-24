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

from gpio import EdgeType, detect_edge, write
from remote.models import (ActuatorParamsResponse, AlarmType, ImageStatus,
                           ProcessImageResponse)
from remote.requests import get_actuator_params, send_alarm, update_status
from utils.config import (ACTUATOR_PIN, ACTUATOR_SENSOR_PIN, QUEUE_MAX_ERRORS,
                          my_logger)
from utils.models import AsyncList


class ActuatorManager:
    def __init__(
        self
    ) -> None:
        self.params: Optional[ActuatorParamsResponse] = None
        self.next_part_to_push: ProcessImageResponse = ProcessImageResponse(
            result= False
        )
        self._error_counter = 0
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

    async def push(self, part: ProcessImageResponse) -> None:
        if self.params is None:
            msg: str = 'Params not loaded. Call await load_params() first.'
            my_logger.critical(msg)
            raise RuntimeError(msg)
        await asyncio.sleep(self.params.actuator_delay / 1000.)
        now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        if now - self.last_push > timedelta(milliseconds= self.params.actuator_cycle_time):
            asyncio.create_task(
                update_status(
                    uuid= part.id,
                    status= ImageStatus.PUSHED
                )
            )
            my_logger.debug(f'Pushing new part with {part}.')
            self.last_push = now
            write(ACTUATOR_PIN, True)
            await asyncio.sleep(0.2)
            write(ACTUATOR_PIN, False)
        else:
            msg: str = f'Part skipped with {part}. Tried to push so early.'
            asyncio.create_task(
                update_status(
                    uuid= part.id,
                    status= ImageStatus.ERROR_SKIPPED
                )
            )
            asyncio.create_task(
                send_alarm(
                    alarm_type= AlarmType.ERROR,
                    message= msg
                )
            )
            my_logger.error(msg)

    async def get_next_result(
        self,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> ProcessImageResponse:
        now: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
        while True:
            try:
                next_result: ProcessImageResponse = await results_queue.check_first()
                self._error_counter = 0
            except asyncio.QueueEmpty:
                msg: str = 'Result lost. There are no results in the queue. The part will be pushed.'
                asyncio.create_task(
                    send_alarm(
                        alarm_type= AlarmType.WARNING,
                        message= msg
                    )
                )
                my_logger.error(msg)
                self._error_counter += 1
                if self._error_counter > QUEUE_MAX_ERRORS:
                    msg: str = 'Tried to recover so many images. Camera failure.'
                    asyncio.create_task(
                        send_alarm(
                            alarm_type= AlarmType.CRITICAL,
                            message= msg
                        )
                    )
                    my_logger.critical(msg)
                return ProcessImageResponse(
                    date= now,
                    result= True
                )
            if now - next_result.date < timedelta(milliseconds= self.sensors_interval_ms * 0.75):
                msg: str = 'Result lost. The part doesn\'t have a result on the queue. The part will be pushed.'
                asyncio.create_task(
                    send_alarm(
                        alarm_type= AlarmType.WARNING,
                        message= msg
                    )
                )
                my_logger.error(msg)
                return ProcessImageResponse(
                    date= now,
                    result= True
                )
            if now - next_result.date > timedelta(milliseconds= self.sensors_interval_ms * 1.25):
                asyncio.create_task(
                    update_status(
                        uuid= next_result.id,
                        status= ImageStatus.ERROR_LOST
                    )
                )
                msg: str = 'Part lost. The part of this result didn\'t reach the actuator.'
                asyncio.create_task(
                    send_alarm(
                        alarm_type= AlarmType.WARNING,
                        message= msg
                    )
                )
                my_logger.error(msg)
                await results_queue.get()
                continue
            result: ProcessImageResponse = await results_queue.get()
            my_logger.debug(f'New part on the actuator with {result}.')
            push: ImageStatus
            if result.result:
                push = ImageStatus.ACTUATOR_PASS
            else:
                push = ImageStatus.ACTUATOR_PUSH
            asyncio.create_task(
                    update_status(
                        uuid= next_result.id,
                        status= push
                    )
                )
            return result

    async def cycle(
        self,
        results_queue: AsyncList[ProcessImageResponse]
    ) -> NoReturn:
        if self.params is None:
            await self.load_params()
        last_sensor_val: bool = False
        edge_type: EdgeType = EdgeType.NONE
        next_part_to_push: Optional[ProcessImageResponse] = None
        try:
            my_logger.info(f'Actuator cycle started.')
            while True:
                await asyncio.sleep(0.001)
                edge_type, last_sensor_val = await detect_edge(
                    pin= ACTUATOR_SENSOR_PIN,
                    last_value= last_sensor_val
                )
                if edge_type == EdgeType.RISING:
                    my_logger.info(f'New part on the actuator.')
                    if next_part_to_push is not None:
                        asyncio.create_task(
                            update_status(
                                uuid= next_part_to_push.id,
                                status= ImageStatus.ERROR_OVERWRITE
                            )
                        )
                        msg: str = 'New part on the actuator without clearing last part.'
                        asyncio.create_task(
                            send_alarm(
                                alarm_type= AlarmType.ERROR,
                                message= msg
                            )
                        )
                        my_logger.error(msg)
                    next_part_to_push = await self.get_next_result(results_queue)
                if edge_type == EdgeType.FALLING:
                    my_logger.debug(f'Part to be pushed with {next_part_to_push}.')
                    if next_part_to_push is not None:
                        if next_part_to_push.result:
                            asyncio.create_task(self.push(next_part_to_push))
                        else:
                            asyncio.create_task(
                                update_status(
                                    uuid= next_part_to_push.id,
                                    status= ImageStatus.PASSED
                                )
                            )
                    next_part_to_push = None
        except asyncio.CancelledError:
            my_logger.info('Actuator cycle cancelled.')
            raise
