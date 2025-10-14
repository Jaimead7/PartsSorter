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

from actuator import actuator_cycle
from camera import CameraManager
from utils.config import CAMERA_INDEX, my_logger
from utils.data_types import Result

results_queue: asyncio.Queue[Result] = asyncio.Queue()

async def main() -> None:
    my_camera = CameraManager(CAMERA_INDEX)
    my_logger.info('Capture starting...')
    await asyncio.gather(
        my_camera.cycle(results_queue),
        actuator_cycle(results_queue),
        return_exceptions= False
    )
    my_logger.info('Capture stopping...')


if __name__ == "__main__":
    asyncio.run(main())
