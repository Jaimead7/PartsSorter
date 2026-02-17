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


from datetime import datetime, timezone
from enum import Enum, unique
from typing import Optional

from pydantic import BaseModel, Field


def now_utc_notz() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CameraParamsResponse(BaseModel):
    camera_width: int = 640
    camera_height: int = 480
    brightness: int = 128
    contrast: int = 32
    saturation: int = 32
    auto_exposure: int = 3
    exposure: int = 40
    auto_wb: int = 1
    wb: int = 0


class ActuatorParamsResponse(BaseModel):
    tape_speed: float = 125 # mm/s
    sensors_distance: float = 345  # mm
    actuator_delay: float = 100 # ms
    actuator_cycle_time: float = 3000 # ms


class ProcessImageResponse(BaseModel):
    date: datetime = Field(default_factory= now_utc_notz)
    id: Optional[str] = None
    result: bool = False

    def __str__(self) -> str:
        formatted_date: str = self.date.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
        id_str: str = f'{self.id}' if self.id is not None else 'Unknown'
        return f'Result(date: {formatted_date}, id: {id_str}, result: {self.result})'


@unique
class ImageStatus(Enum):
    CAPTURED = 0
    TRANSITION_PUSH = 1
    TRANSITION_PASS = 2
    ACTUATOR_PUSH = 3
    ACTUATOR_PASS = 4
    PUSHED = 5
    PASSED = 6
    ERROR_OVERWRITE = -1
    ERROR_LOST = -2
    ERROR_SKIPPED = -3
