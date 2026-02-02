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


from fastapi import APIRouter, WebSocket

from ..dependencies.config import my_logger
from ..dependencies.web_sockets import ImageStreamSocketManager

ws_router = APIRouter()

@ws_router.websocket(
    "/image-stream/",
    name= 'Image stream socket'
)
async def websocket_endpoint(websocket: WebSocket) -> None:
    await ImageStreamSocketManager.connect(websocket)
    try:
        while True:
            await websocket.receive_bytes()
    except Exception as e:
        my_logger.error(f"WebSocket error: {e}")
    finally:
        await ImageStreamSocketManager.disconnect(websocket)
