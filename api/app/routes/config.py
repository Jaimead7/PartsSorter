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


from fastapi import APIRouter, status

from ..dependencies.config import HOST_IP, SERVER_PORT
from ..models.api import ApiIPResponse

config_router = APIRouter()

@config_router.get(
    '/ip',
    response_model= ApiIPResponse,
    summary= 'Get the API IP.',
    response_description= 'The API IP.',
    status_code= status.HTTP_200_OK
)
async def get_API_URL() -> ApiIPResponse:
    return ApiIPResponse(ip= f'{HOST_IP}:{SERVER_PORT}')
