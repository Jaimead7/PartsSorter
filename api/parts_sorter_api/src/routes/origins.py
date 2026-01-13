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

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.origins import (db_create_new_origin, db_delete_origin_params,
                                db_delete_origins, db_get_origin,
                                db_get_origin_camera_params,
                                db_get_origin_images,
                                db_get_origin_origin_result,
                                db_get_origin_params, db_get_origins,
                                db_update_origin, db_update_origin_params)
from ..dependencies.config import DATABASE_GET_LIMIT
from ..models.api import CameraParams
from ..models.database import Image, Origin, OriginResult

origins_router: APIRouter = APIRouter()

@origins_router.post(
    '/',
    response_model= Origin,
    summary= 'Create new Origin on the database.',
    response_description= 'The new Origin created.'
)
async def create_new_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[Origin, Body()]
) -> Origin:
    return await db_create_new_origin(
        session= session,
        origin= origin
    )

@origins_router.delete(
    '/',
    summary= 'Delete Origin\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_origins(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: Annotated[list[str], Query()] = []
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
    names: Annotated[list[str], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[Origin]:
    return await db_get_origins(
        session= session,
        origins= [Origin(name= name) for name in names],
        limit= limit,
        offset= offset
    )

@origins_router.put(
    '/{name}/',
    response_model= Origin,
    summary= 'Update Origin on the database.',
    response_description= 'The Origin updated.',
    status_code= status.HTTP_200_OK
)
async def update_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    model: Annotated[Optional[str], Body()] = None,
    params: Annotated[Optional[dict[str, Any]], Body()] = None
) -> Origin:
    return await db_update_origin(
        session= session,
        origin= Origin(
            name= name,
            model= model,
            params= params
        )
    )

@origins_router.delete(
    '/{name}/',
    summary= 'Delete Origin from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> None:
    await db_delete_origins(
        session= session,
        origins= [Origin(name= name)]
    )

@origins_router.get(
    '/{name}/',
    response_model= list[Origin],
    summary= 'Get Origin of the database.',
    response_description= 'The Origin list.',
    status_code= status.HTTP_200_OK
)
async def get_origin(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> Origin:
    return await db_get_origin(
        session= session,
        origin= Origin(name= name)
    )

@origins_router.get(
    '/{name}/images/',
    response_model= list[Image],
    summary= 'Get the Image\'s of an Origin of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_origin_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Optional[list[Image]]:
    return await db_get_origin_images(
        session= session,
        origin_name= name,
        limit= limit,
        offset= offset
    )

@origins_router.get(
    '/{name}/origin-results/',
    response_model= list[OriginResult],
    summary= 'Get the OriginResult\'s of an Origin of the database.',
    response_description= 'The OriginResult\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_origin_origin_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Optional[list[OriginResult]]:
    return await db_get_origin_origin_result(
        session= session,
        origin_name= name,
        limit= limit,
        offset= offset
    )

@origins_router.get(
    '/{name}/camera-params/',
    response_model= CameraParams,
    summary= 'Get the parameters of the camera from a origin.',
    response_description= 'The camera parameters.',
    status_code= status.HTTP_200_OK
)
async def get_origin_camera_params(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> CameraParams:
    return await db_get_origin_camera_params(
        session= session,
        origin_name = name
    )

@origins_router.get(
    '/{name}/params/',
    response_model= dict[str, Any],
    summary= 'Delete the params of the origin.',
    response_description= 'The origin params.',
    status_code= status.HTTP_200_OK
)
async def get_origin_params(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> dict[str, Any]:
    return await db_get_origin_params(
        session= session,
        origin_name = name
    )

@origins_router.put(
    '/{name}/params/',
    response_model= Origin,
    summary= 'Delete the params of the origin.',
    response_description= 'The origin params.',
    status_code= status.HTTP_200_OK
)
async def put_origin_params(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    params: Annotated[Optional[dict[str, Any]], Body(embed= True)] = None
) -> Origin:
    return await db_update_origin_params(
        session= session,
        origin_name = name,
        params= params
    )

@origins_router.delete(
    '/{name}/params/',
    response_model= Origin,
    summary= 'Delete the params of the origin.',
    response_description= 'The origin params.',
    status_code= status.HTTP_200_OK
)
async def delete_origin_params(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> Origin:
    return await db_delete_origin_params(
        session= session,
        origin_name = name
    )
