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
from ..dependencies.config import DATABASE_GET_LIMIT
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

@inspection_results_router.put(
    '/{name}/',
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
    '/{name}/',
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

@inspection_results_router.get(
    '/{name}/',
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
    '/{name}/images/',
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
    '/{name}/model-classes/',
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
    '/{name}/origin-results/',
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
