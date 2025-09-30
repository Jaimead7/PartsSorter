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


#---------- LOAD ENV VARIABLES FIRST ----------#
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(
    Path(__file__).parents[1] / 'dist' / '.env',
    override= False
)
#---------------------------------------------#

import asyncio

from actuator import actuator_cycle
from camera import camera_cycle
from utils.config import my_logger
from utils.data_types import Result

results_queue: asyncio.Queue[Result] = asyncio.Queue()

async def main() -> None:
    my_logger.info('Capture starting...')
    await asyncio.gather(
        camera_cycle(results_queue),
        actuator_cycle(results_queue)
    )
    my_logger.info('Capture stopping...')


if __name__ == "__main__":
    asyncio.run(main())
