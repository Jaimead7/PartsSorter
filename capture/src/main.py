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
