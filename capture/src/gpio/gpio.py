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
            from gpiod.line import Direction
        except ImportError:
            my_logger.error('"gpiod" not installed. Can\'t read on GPIO pins.')
            return None
        with gpiod.request_lines(
            cls.get_chip(),
            consumer= 'Me',
            config= {
                pin: gpiod.LineSettings(
                    direction= Direction.INPUT
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
