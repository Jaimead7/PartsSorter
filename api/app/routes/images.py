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

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.images import (db_create_new_image, db_delete_images,
                               db_get_images, db_process_new_image,
                               db_update_image)
from ..database.manager import get_session
from ..database.origin_results import db_get_origin_result
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import Image, ImageProcessed, OriginResult

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
    origin: Optional[str] = None
) -> Image:
    """Create new image on the database.  
    - Args:  
        - files (UploadFile): File of the Image to create.  
        - origin (Optional[str]): Origin of the image.  
    - Returns:  
        - Image: Image created.  
    """
    return await db_create_new_image(
        session= session,
        file= file,
        origin= origin
    )

@images_router.put(
    '/',
    response_model= Image,
    summary= 'Update Image on the database.',
    response_description= 'The Image updated.',
    status_code= status.HTTP_200_OK
)
async def update_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuid: UUID,
    inspection_result: Optional[str],
    origin: Optional[str]
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
    '/',
    summary= 'Delete Image from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: list[UUID] = Query([])
) -> None:
    """Delete Image from database.  
    - Args:  
        - uuids: list[UUID]: Images to be deleted (Deleted by id).  
    - Raises:  
        - HTTPException: ID not found.  
    """
    images: list[Any] = [Image(id= uuid) for uuid in uuids]
    await db_delete_images(
        session= session,
        images= images
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
    uuids: list[UUID] = Query([]),
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> Sequence[Image]:
    """Get Image\'s from the database.  
    - Args:  
        - uuids (list[UUID], optional): List of the Image\'s uuids to read. If empty get all. Defaults to Query([]).  
        - limit (int, optional): Max numbre of values to return. Defaults to DATABASE_GET_LIMIT.  
        - offset (int, optional): Offset of the SELECT. Defaults to 0.  
    - Raises:  
        - HTTPException: If Image\'s not found raise HTTP 404.  
    - Returns:  
        - Sequence[Image]: List of Image\'s readed.  
    """
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
    origin: Optional[str] = None
) -> ImageProcessed:
    return await db_process_new_image(
        session= session,
        file= file,
        origin= origin
    )
