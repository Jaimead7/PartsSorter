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


from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import (APIRouter, BackgroundTasks, Body, Depends, Path, Query,
                     UploadFile, status)
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.images import (db_create_and_process_new_image,
                               db_create_new_image, db_delete_images_by_id,
                               db_get_image_by_id, db_get_image_extensions,
                               db_get_images_by_ids, db_get_next_hist_image,
                               db_update_image)
from ..database.manager import get_session
from ..dependencies.config import DATABASE_GET_LIMIT
from ..dependencies.web_sockets import ImageStreamSocketManager
from ..models.api import (ImageFilters, ImageHistResponse,
                          ImageProcessedResponse, ImageResponse,
                          ImageStatusResponse)
from ..models.database import Image, ImageStatus

images_router: APIRouter = APIRouter()

@images_router.post(
    '/',
    response_model= ImageResponse,
    summary= 'Create new Image on the database.',
    response_description= 'The new Image created.',
    status_code= status.HTTP_201_CREATED
)
async def create_new_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    file: UploadFile,
    origin: Annotated[Optional[str], Body(embed= True)] = None
) -> ImageResponse:
    db_image: Image = await db_create_new_image(
        session= session,
        file= file,
        origin_name= origin
    )
    return ImageResponse.from_image(
        image= db_image
    )

@images_router.get(
    '/',
    response_model= Sequence[ImageResponse],
    summary= 'Get Image\'s of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: Annotated[list[UUID], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[ImageResponse]:
    db_images: Sequence[Image] = await db_get_images_by_ids(
        session= session,
        images_uuids= uuids,
        limit= limit,
        offset= offset
    )
    return [ImageResponse.from_image(image= img) for img in db_images]

@images_router.delete(
    '/',
    summary= 'Delete Image\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: Annotated[list[UUID], Body(embed= True)]
) -> None:
    await db_delete_images_by_id(
        session= session,
        images_uuids= uuids
    )

@images_router.post(
    '/process/',
    response_model= ImageProcessedResponse,
    summary= 'Process new Image and save it to the database.',
    response_description= 'The new Image created.',
    status_code= status.HTTP_201_CREATED
)
async def process_new_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    bg_tasks: BackgroundTasks,
    file: UploadFile,
    origin: Annotated[Optional[str], Body(embed= True)] = None
) -> ImageProcessedResponse:
    db_image: Image
    result: bool
    db_image, result = await db_create_and_process_new_image(
        session= session,
        file= file,
        origin_name= origin
    )
    response: ImageProcessedResponse = ImageProcessedResponse.from_image(
        image= db_image,
        result= result
    )
    bg_tasks.add_task(
        ImageStreamSocketManager.broadcast,
        response
    )
    return response

@images_router.get(
    '/hist/next/',
    response_model= ImageHistResponse,
    summary= 'Get the next image of the database.',
    response_description= 'The Image data.',
    status_code= status.HTTP_200_OK
)
async def get_next_hist_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    extension: Annotated[list[str], Query()] = [],
    start_date: Annotated[Optional[datetime], Query()] = None,
    end_date: Annotated[Optional[datetime], Query()] = None,
    inspection_result: Annotated[list[Optional[str]], Query()] = [],
    origin: Annotated[list[Optional[str]], Query()] = [],
    model: Annotated[list[Optional[str]], Query()] = [],
    true_result: Annotated[list[Optional[str]], Query()] = [],
    min_trust: Annotated[Optional[float], Query()] = None,
    max_trust: Annotated[Optional[float], Query()] = None,
    status: Annotated[list[str], Query()] = [],
    index: Annotated[int, Query()] = 0
)-> ImageHistResponse:
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
        status= status
    )
    db_image: Image
    i: int
    total: int
    db_image, i, total = await db_get_next_hist_image(
        session= session,
        filters= filters,
        index= index
    )
    return ImageHistResponse.from_image(
        image= db_image,
        index= i,
        total= total
    )

@images_router.get(
    '/extensions/',
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

@images_router.get(
    '/{uuid}/',
    response_model= ImageResponse,
    summary= 'Get an Image of the database.',
    response_description= 'The Image list.',
    status_code= status.HTTP_200_OK
)
async def get_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()]
) -> ImageResponse:
    db_image: Image = await db_get_image_by_id(
        session= session,
        image= Image(id= uuid)
    )
    return ImageResponse.from_image(
        image= db_image
    )

@images_router.delete(
    '/{uuid}/',
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

@images_router.put(
    '/{uuid}/',
    response_model= ImageResponse,
    summary= 'Update Image on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()],
    inspection_result: Annotated[Optional[str], Body(embed= True)] = None,
    origin: Annotated[Optional[str], Body(embed= True)] = None,
    true_result: Annotated[Optional[str], Body(embed= True)] = None,
    trust: Annotated[Optional[float], Body(embed= True)] = None,
    status: Annotated[int, Body(embed= True)] = ImageStatus.captured
) -> ImageResponse:
    image = Image(
        id= uuid,
        inspection_result= inspection_result,
        origin= origin,
        true_result= true_result,
        trust= trust,
        status= status
    )
    db_image: Image = await db_update_image(
        session= session,
        image= image,
    )
    return ImageResponse.from_image(
        image= db_image
    )

@images_router.put(
    '/{uuid}/true-result/',
    response_model= ImageResponse,
    summary= 'Update Image.true_result on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image_true_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: Annotated[UUID, Path()],
    true_result: Annotated[Optional[str], Body(embed= True)] = None,
) -> ImageResponse:
    db_image: Image = await db_get_image_by_id(
        session= session,
        image= Image(id= uuid)
    )
    db_image.true_result = true_result
    db_image = await db_update_image(
        session= session,
        image= db_image,
        update_date= False
    )
    return ImageResponse.from_image(
        image= db_image
    )

@images_router.put(
    '/{uuid}/status/',
    response_model= ImageStatusResponse,
    summary= 'Update Image.status on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image_status(
    session: Annotated[AsyncSession, Depends(get_session)],
    bg_tasks: BackgroundTasks,
    uuid: Annotated[UUID, Path()],
    status: Annotated[str | int, Body(embed= True)] = ImageStatus.captured,
) -> ImageStatusResponse:
    db_image: Image = await db_get_image_by_id(
        session= session,
        image= Image(id= uuid)
    )
    db_image.status = ImageStatus.get_value(status)
    db_image = await db_update_image(
        session= session,
        image= db_image,
        update_date= False
    )
    image_status: ImageStatusResponse = ImageStatusResponse.from_image(
        image= db_image
    )
    bg_tasks.add_task(
        ImageStreamSocketManager.broadcast,
        image_status
    )
    return image_status
