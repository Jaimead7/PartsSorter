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
import signal
import sys
from typing import NoReturn

from actuator import ActuatorManager
from camera import CameraManager
from remote.models import ProcessImageResponse
from utils.config import CAMERA_DEVICE, my_logger
from utils.models import AsyncList

results_queue: AsyncList[ProcessImageResponse] = AsyncList()

async def main() -> None:
    my_logger.info('Capture starting...')
    camera_task: asyncio.Task[NoReturn] = asyncio.create_task(
        CameraManager(CAMERA_DEVICE).cycle(results_queue)
    )
    actuator_task: asyncio.Task[NoReturn] = asyncio.create_task(
        ActuatorManager().cycle(results_queue)
    )

    def signal_handler() -> None:
        my_logger.info('Received shutdown signal.')
        camera_task.cancel()
        actuator_task.cancel()

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, signal_handler)
    try:
        await asyncio.gather(
            camera_task,
            actuator_task,
            return_exceptions=False
        )
    except asyncio.CancelledError:
        my_logger.info('Tasks cancelled.')
    except Exception as e:
        my_logger.error(f'Error in main: {e}.')
        raise
    finally:
        my_logger.info('Capture stopping...')

if __name__ == "__main__":
    try:
        asyncio.run(main())
        my_logger.info('Application shutdown completed successfully.')
        sys.exit(0)
    except Exception as e:
        my_logger.error(f'Application error: {e}.')
        sys.exit(1)
