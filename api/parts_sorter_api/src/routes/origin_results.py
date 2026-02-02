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


from typing import Annotated, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.origin_results import (db_create_new_origin_result,
                                       db_delete_origin_result,
                                       db_get_origin_results,
                                       db_update_origin_result)
from ..dependencies.config import DATABASE_GET_LIMIT
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

@origin_results_router.put(
    '/{origin}/{inspection_result}/',
    response_model= OriginResult,
    summary= 'Update OriginResult on the database.',
    response_description= 'The OriginResult updated.',
    status_code= status.HTTP_200_OK
)
async def update_origin_result(
    session: Annotated[AsyncSession, Depends(get_session)],
    origin: Annotated[str, Path()],
    inspection_result: Annotated[str, Path()],
    result: Annotated[bool, Body()],
    threshold: Annotated[float, Body()]
) -> OriginResult:
    return await db_update_origin_result(
        session= session,
        origin_result= OriginResult(
            origin= origin,
            inspection_result= inspection_result,
            result= result,
            threshold= threshold
        )
    )

@origin_results_router.delete(
    '/{origin}/{inspection_result}/',
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
