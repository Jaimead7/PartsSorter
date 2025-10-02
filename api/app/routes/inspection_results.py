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


from typing import Annotated, Optional, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.inspection_results import (
    db_create_new_inspection_result, db_delete_inspection_results,
    db_get_inspection_result, db_get_inspection_result_images,
    db_get_inspection_result_model_classes,
    db_get_inspection_result_origin_results, db_get_inspection_results,
    db_update_inspection_result)
from ..database.manager import get_session
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import Image, InspectionResult, ModelClass, OriginResult

inspection_results_router = APIRouter()

@inspection_results_router.post(
    '/',
    response_model= InspectionResult,
    summary= 'Create new InspectionResult on the database.',
    response_description= 'The new InspectionResult created.'
)
async def create_new_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Body()]
) -> InspectionResult:
    return await db_create_new_inspection_result(
        session= session,
        name= name
    )

@inspection_results_router.put(
    '/{name}',
    response_model= InspectionResult,
    summary= 'Update InspectionResult on the database.',
    response_description= 'The InspectionResult updated.',
    status_code= status.HTTP_200_OK
)
async def update_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> InspectionResult:
    return await db_update_inspection_result(
        session= session,
        inspection_result= InspectionResult(name= name)
    )

@inspection_results_router.delete(
    '/{name}',
    summary= 'Delete InspectionResult from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> None:
    await db_delete_inspection_results(
        session= session,
        inspection_results= [InspectionResult(name= name)]
    )

@inspection_results_router.delete(
    '/',
    summary= 'Delete InspectionResult\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_inspection_results(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: Annotated[list[str], Query()] = []
) -> None:
    inspection_result: list[InspectionResult] = [InspectionResult(name= name) for name in names]
    await db_delete_inspection_results(
        session= session,
        inspection_results= inspection_result
    )

@inspection_results_router.get(
    '/{name}',
    response_model= list[InspectionResult],
    summary= 'Get InspectionResult of the database.',
    response_description= 'The InspectionResult list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> InspectionResult:
    return await db_get_inspection_result(
        session= session,
        inspection_result= InspectionResult(name= name)
    )

@inspection_results_router.get(
    '/',
    response_model= list[InspectionResult],
    summary= 'Get InspectionResult\'s of the database.',
    response_description= 'The InspectionResult\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_results(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: Annotated[list[str], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[InspectionResult]:
    return await db_get_inspection_results(
        session= session,
        inspection_results= [InspectionResult(name= name) for name in names],
        limit= limit,
        offset= offset
    )

@inspection_results_router.get(
    '/{name}/images',
    response_model= list[Image],
    summary= 'Get the Image\'s of an InspectionResult of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_result_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Optional[list[Image]]:
    return await db_get_inspection_result_images(
        session= session,
        inspection_result_name= name,
        limit= limit,
        offset= offset
    )

@inspection_results_router.get(
    '/{name}/model-classes',
    response_model= list[ModelClass],
    summary= 'Get the ModelClass\'s of an InspectionResult of the database.',
    response_description= 'The ModelClass\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_result_model_classes(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Optional[list[ModelClass]]:
    return await db_get_inspection_result_model_classes(
        session= session,
        inspection_result_name= name,
        limit= limit,
        offset= offset
    )

@inspection_results_router.get(
    '/{name}/origin-results',
    response_model= list[OriginResult],
    summary= 'Get the OriginResult\'s of an InspectionResult of the database.',
    response_description= 'The OriginResult\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_result_origin_results(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Optional[list[OriginResult]]:
    return await db_get_inspection_result_origin_results(
        session= session,
        inspection_result_name= name,
        limit= limit,
        offset= offset
    )
