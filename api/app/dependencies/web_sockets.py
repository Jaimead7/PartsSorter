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


from typing import Optional

from fastapi import WebSocket
from pyUtils import NoInstantiable

from ..models.api import ImageStreamResponse
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
        image_url: str,
        insp_result: Optional[str],
        origin: Optional[str]
    ) -> None:
        response: ImageStreamResponse = ImageStreamResponse.factory(
            image_url= image_url,
            insp_result= insp_result,
            origin= origin
        )
        for socket in cls._active_sockets:
            try:
                await socket.send_json(response.model_dump())
            except Exception as e:
                my_logger.error(f'Error sending message to client: {e}')
                cls._active_sockets.remove(socket)
