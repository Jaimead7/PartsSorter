# Copyright 2025 Jaime Álvarez

# MIT License
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


from typing import Literal, Optional

from utils.config import GPIO_CHIP, my_logger


class GPIO:
    @classmethod
    def write(cls, pin: int, status: bool = False) -> None:
        try:
            import gpiod
            from gpiod.line import Direction, Value
        except ImportError:
            my_logger.error('"gpiod" not installed. Can\'t write on GPIO pins.')
            return
        with gpiod.request_lines(
            cls.get_chip(),
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

    @classmethod
    def read(cls, pin: int) -> Optional[bool]:
        try:
            import gpiod
            from gpiod.line import Bias, Direction
        except ImportError:
            my_logger.error('"gpiod" not installed. Can\'t read on GPIO pins.')
            return None
        with gpiod.request_lines(
            cls.get_chip(),
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

    @classmethod
    def get_chip(cls) -> str:
        if GPIO_CHIP is None:
            msg: str = f'"{GPIO_CHIP}" not found in environmental variables.'
            my_logger.error(msg)
            raise ValueError(msg)
        return GPIO_CHIP
