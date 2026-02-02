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


from fastapi import WebSocket
from pyUtils import NoInstantiable

from ..models.api import ImageStreamResponse
from ..models.database import Image
from .config import my_logger


class ImageStreamSocketManager(NoInstantiable):
    _active_sockets: list[WebSocket] = []

    @classmethod
    async def connect(cls, websocket: WebSocket) -> None:
        await websocket.accept()
        cls._active_sockets.append(websocket)

    @classmethod
    async def disconnect(cls, websocket: WebSocket) -> None:
        cls._active_sockets.remove(websocket)

    @classmethod
    async def broadcast_new_result(
        cls,
        image: Image
    ) -> None:
        response: ImageStreamResponse = ImageStreamResponse.from_image(
            image= image
        )
        for socket in cls._active_sockets:
            try:
                await socket.send_json(response.model_dump())
            except Exception as e:
                my_logger.error(f'Error sending message to client: {e}')
                cls._active_sockets.remove(socket)
