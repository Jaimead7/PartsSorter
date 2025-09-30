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


from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.origins import (db_create_new_origin, db_delete_origins,
                                db_get_origin_images, db_get_origins,
                                db_update_origin)
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import Image, Origin

origins_router = APIRouter()

@origins_router.post(
    '/',
    response_model= Origin,
    summary= 'Create new Origin on the database.',
    response_description= 'The new Origin created.'
)
async def create_new_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[Origin, Query()]
) -> Origin:
    return await db_create_new_origin(
        session= session,
        origin= origin
    )

@origins_router.put(
    '/',
    response_model= Origin,
    summary= 'Update Origin on the database.',
    response_description= 'The Origin updated.',
    status_code= status.HTTP_200_OK
)
async def update_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[Origin, Query()]
) -> Origin:
    return await db_update_origin(
        session= session,
        origin= origin
    )

@origins_router.delete(
    '/',
    summary= 'Delete Origin from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_origins(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: list[str] = Query([])
) -> None:
    origins: list[Origin] = [Origin(name= name) for name in names]
    await db_delete_origins(
        session= session,
        origins= origins
    )

@origins_router.get(
    '/',
    response_model= list[Origin],
    summary= 'Get Origin\'s of the database.',
    response_description= 'The Origin\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_origins(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: list[str] = Query([]),
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> Sequence[Origin]:
    return await db_get_origins(
        session= session,
        origins= [Origin(name= name) for name in names],
        limit= limit,
        offset= offset
    )

@origins_router.get(
    '/{name}/images',
    response_model= list[Image],
    summary= 'Get the images of an Origin of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_origin_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str,
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> list[Image] | None:
    return await db_get_origin_images(
        session= session,
        origin_name= name,
        limit= limit,
        offset= offset
    )
