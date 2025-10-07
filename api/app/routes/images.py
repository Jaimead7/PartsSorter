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


from typing import Annotated, Any, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.images import (db_create_new_image, db_delete_images,
                               db_get_image, db_get_images,
                               db_process_new_image, db_update_image)
from ..database.manager import get_session
from ..dependencies.server_config import DATABASE_GET_LIMIT
from ..models.database import Image, ImageProcessed

images_router = APIRouter()

@images_router.post(
    '/',
    response_model= Image,
    summary= 'Create new Image on the database.',
    response_description= 'The new Image created.',
    status_code= status.HTTP_201_CREATED
)
async def create_new_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    file: UploadFile,
    origin: Annotated[Optional[str], Body()] = None
) -> Image:
    return await db_create_new_image(
        session= session,
        file= file,
        origin= origin
    )

@images_router.put(
    '/{uuid}',
    response_model= Image,
    summary= 'Update Image on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()],
    inspection_result: Annotated[Optional[str], Body()] = None,
    origin: Annotated[Optional[str], Body()] = None
) -> Image:
    image = Image(
        id= uuid,
        inspection_result= inspection_result,
        origin= origin
    )
    return await db_update_image(
        session= session,
        image= image,
    )

@images_router.delete(
    '/{uuid}',
    summary= 'Delete Image from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()]
) -> None:
    await db_delete_images(
        session= session,
        images= [Image(id= uuid)]
    )

@images_router.delete(
    '/',
    summary= 'Delete Image\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: Annotated[list[UUID], Body()]
) -> None:
    images: list[Any] = [Image(id= uuid) for uuid in uuids]
    await db_delete_images(
        session= session,
        images= images
    )

@images_router.get(
    '/{uuid}',
    response_model= list[Image],
    summary= 'Get an Image of the database.',
    response_description= 'The Image list.',
    status_code= status.HTTP_200_OK
)
async def get_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()]
) -> Image:
    return await db_get_image(
        session= session,
        image= Image(id= uuid)
    )

@images_router.get(
    '/',
    response_model= list[Image],
    summary= 'Get Image\'s of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: Annotated[list[UUID], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[Image]:
    return await db_get_images(
        session= session,
        images= [Image(id= uuid) for uuid in uuids],
        limit= limit,
        offset= offset
    )

@images_router.post(
    '/process',
    response_model= ImageProcessed,
    summary= 'Process new Image and save it to the database.',
    response_description= 'The new Image created.',
    status_code= status.HTTP_201_CREATED
)
async def process_new_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    file: UploadFile,
    origin: Annotated[Optional[str], Body()] = None
) -> ImageProcessed:
    return await db_process_new_image(
        session= session,
        file= file,
        origin_name= origin
    )
