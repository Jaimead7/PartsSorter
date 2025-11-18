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


from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.images import (db_create_and_process_new_image,
                               db_create_new_image, db_delete_images_by_id,
                               db_get_image_by_id, db_get_image_extensions,
                               db_get_images_by_ids, db_get_next_hist_image,
                               db_update_image)
from ..database.manager import get_session
from ..dependencies.config import DATABASE_GET_LIMIT
from ..models.api import ImageFilters, ImageHistResponse, ImageStreamResponse
from ..models.database import Image, ImageProcessed

images_router: APIRouter = APIRouter()

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
        origin_name= origin
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
    return await db_get_images_by_ids(
        session= session,
        images_uuids= uuids,
        limit= limit,
        offset= offset
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
    await db_delete_images_by_id(
        session= session,
        images_uuids= images
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
    return await db_create_and_process_new_image(
        session= session,
        file= file,
        origin_name= origin
    )

@images_router.get(
    '/hist/next',
    response_model= ImageHistResponse,
    summary= 'Get the next image of the database.',
    response_description= 'The Image data.',
    status_code= status.HTTP_200_OK
)
async def get_next_hist_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    extension: Annotated[list[str], Query()] = [],
    start_date: Annotated[datetime, Query()] = datetime.now(timezone.utc) - timedelta(days=30),
    end_date: Annotated[datetime, Query()] = datetime.now(timezone.utc),
    inspection_result: Annotated[list[Optional[str]], Query()] = [],
    origin: Annotated[list[str], Query()] = [],
    model: Annotated[list[str], Query()] = [],
    true_result: Annotated[list[Optional[str]], Query()] = [],
    min_trust: Annotated[float, Query()] = 0.,
    max_trust: Annotated[float, Query()] = 1.,
    index: Annotated[int, Query()] = 0
)-> ImageHistResponse:
    inspection_result = [
        None
        if result == 'No result'
        else result
        for result in inspection_result
    ]
    true_result = [
        None
        if result == 'No result'
        else result
        for result in true_result
    ]
    filters: ImageFilters = ImageFilters(
        extensions= extension,
        start_date= start_date,
        end_date= end_date,
        inspection_results= inspection_result,
        origins= origin,
        models= model,
        true_results= true_result,
        min_trust= min_trust,
        max_trust= max_trust,
    )
    return await db_get_next_hist_image(
        session= session,
        filters= filters,
        index= index
    )

@images_router.get(
    '/extensions',
    response_model= list[str],
    summary= 'Get all extensions of the Images of the database.',
    response_description= 'The extensions list.',
    status_code= status.HTTP_200_OK
)
async def get_image_extensions(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Sequence[str]:
    return await db_get_image_extensions(
        session= session
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
    origin: Annotated[Optional[str], Body()] = None,
    true_result: Annotated[Optional[str], Body()] = None,
    trust: Annotated[Optional[float], Body()] = None 
) -> Image:
    image = Image(
        id= uuid,
        inspection_result= inspection_result,
        origin= origin,
        true_result= true_result,
        trust= trust
    )
    return await db_update_image(
        session= session,
        image= image,
    )

@images_router.put(
    '/{uuid}/true-result',
    response_model= ImageStreamResponse,
    summary= 'Update Image.true_result on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image_true_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()],
    true_result: Annotated[Optional[str], Body()] = None,
) -> ImageStreamResponse:
    image: Image = await db_get_image_by_id(
        session= session,
        image= Image(id= uuid)
    )
    image.true_result = true_result
    image = await db_update_image(
        session= session,
        image= image,
        update_date= False
    )
    return ImageStreamResponse.from_image(image= image)

@images_router.delete(
    '/{uuid}',
    summary= 'Delete Image from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()]
) -> None:
    await db_delete_images_by_id(
        session= session,
        images_uuids= [uuid]
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
    return await db_get_image_by_id(
        session= session,
        image= Image(id= uuid)
    )
