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
from enum import Enum
from typing import Literal, Optional

from utils.config import GPIO_CHIP, my_logger


def write(pin: int, status: bool = False) -> None:
    try:
        import gpiod
        from gpiod.line import Direction, Value
    except ImportError:
        my_logger.error('"gpiod" not installed. Can\'t write on GPIO pins.')
        return
    with gpiod.request_lines(
        GPIO_CHIP,
        consumer= 'Me',
        config= {
            pin: gpiod.LineSettings(
                direction= Direction.OUTPUT,
            )
        }
    ) as chip:
        def get_value(flag: bool) -> Literal[Value.ACTIVE] | Literal[Value.INACTIVE]:
            if flag:
                return Value.ACTIVE
            return Value.INACTIVE
        chip.set_value(pin, get_value(status))
        #my_logger.debug(f'Writed to PIN-{pin}: {status}.')

def read(pin: int) -> Optional[bool]:
    try:
        import gpiod
        from gpiod.line import Bias, Direction
    except ImportError:
        my_logger.error('"gpiod" not installed. Can\'t read on GPIO pins.')
        return None
    with gpiod.request_lines(
        GPIO_CHIP,
        consumer= 'Me',
        config= {
            pin: gpiod.LineSettings(
                direction= Direction.INPUT,
                bias= Bias.PULL_DOWN
            )
        }
    ) as chip:
        result: bool = bool(chip.get_value(pin))
        #my_logger.debug(f'Readed from PIN-{pin}: {result}.')
        return result

class EdgeType(Enum):
    NONE = 0
    RISING = 1
    FALLING = 2

async def detect_edge(pin: int, last_value: bool) -> tuple[EdgeType, bool]:
    current_value: list[Optional[bool]] = [None, None]
    current_value[0] = read(pin)
    await asyncio.sleep(0.01)
    current_value[1] = read(pin)
    if current_value[0] == current_value[1]:
        value_filter: bool = all(current_value)
    else:
        value_filter = last_value
    if value_filter and not last_value:
        return EdgeType.RISING, value_filter
    if not value_filter and last_value:
        return EdgeType.FALLING, value_filter
    return EdgeType.NONE, value_filter
