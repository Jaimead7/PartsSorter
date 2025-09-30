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

from ..database.inspection_results import (db_create_new_inspection_result,
                                           db_delete_inspection_results,
                                           db_get_inspection_result_images,
                                           db_get_inspection_results,
                                           db_update_inspection_result)
from ..database.manager import get_session
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import Image, InspectionResult

inspection_results_router = APIRouter()

@inspection_results_router.post(
    '/',
    response_model= InspectionResult,
    summary= 'Create new InspectionResult on the database.',
    response_description= 'The new InspectionResult created.'
)
async def create_new_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str
) -> InspectionResult:
    return await db_create_new_inspection_result(
        session= session,
        name= name
    )

@inspection_results_router.put(
    '/',
    response_model= InspectionResult,
    summary= 'Update InspectionResult on the database.',
    response_description= 'The InspectionResult updated.',
    status_code= status.HTTP_200_OK
)
async def update_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    inspection_result: Annotated[InspectionResult, Query()]
) -> InspectionResult:
    return await db_update_inspection_result(
        session= session,
        inspection_result= inspection_result
    )

@inspection_results_router.delete(
    '/',
    summary= 'Delete InspectionResult from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_inspection_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: list[str] = Query([])
) -> None:
    inspection_result: list[InspectionResult] = [InspectionResult(name= name) for name in names]
    await db_delete_inspection_results(
        session= session,
        inspection_results= inspection_result
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
    names: list[str] = Query([]),
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
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
    summary= 'Get the images of an InspectionResult of the database.',
    response_description= 'The Image\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_inspection_result_images(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str,
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> list[Image] | None:
    return await db_get_inspection_result_images(
        session= session,
        inspection_result_name= name,
        limit= limit,
        offset= offset
    )
