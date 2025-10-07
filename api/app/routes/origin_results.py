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


from typing import Annotated, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.origin_results import (db_create_new_origin_result,
                                       db_delete_origin_result,
                                       db_get_origin_results,
                                       db_update_origin_result)
from ..dependencies.server_config import DATABASE_GET_LIMIT
from ..models.database import OriginResult

origin_results_router = APIRouter()


@origin_results_router.post(
    '/',
    response_model= OriginResult,
    summary= 'Create new OriginResult on the database.',
    response_description= 'The new OriginResult created.',
    status_code= status.HTTP_201_CREATED
)
async def create_new_origin_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin_result: Annotated[OriginResult, Body()]
) -> OriginResult:
    return await db_create_new_origin_result(
        session= session,
        origin_result= origin_result
    )

@origin_results_router.put(
    '/{origin}/{inspection_result}',
    response_model= OriginResult,
    summary= 'Update OriginResult on the database.',
    response_description= 'The OriginResult updated.',
    status_code= status.HTTP_200_OK
)
async def update_origin_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[str, Path()],
    inspection_result: Annotated[str, Path()],
    result: Annotated[bool, Body()]
) -> OriginResult:
    return await db_update_origin_result(
        session= session,
        origin_result= OriginResult(
            origin= origin,
            inspection_result= inspection_result,
            result= result
        )
    )

@origin_results_router.delete(
    '/{origin}/{inspection_result}',
    summary= 'Delete OriginResult from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_origin_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[str, Path()],
    inspection_result: Annotated[str, Path()],
) -> None:
    origin_result: OriginResult = OriginResult(
        origin= origin,
        inspection_result= inspection_result
    )
    await db_delete_origin_result(
        session= session,
        origin_result= origin_result
    )

@origin_results_router.get(
    '/',
    response_model= list[OriginResult],
    summary= 'Get OriginResult\'s of the database.',
    response_description= 'The OriginResult\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_origin_results(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[OriginResult]:
    return await db_get_origin_results(
        session= session,
        limit= limit,
        offset= offset
    )
