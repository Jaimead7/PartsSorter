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


from typing import Sequence

from fastapi import HTTPException, status
from pyUtils import Styles
from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..dependencies.config import my_logger
from ..models.database import OriginResult


async def db_create_new_origin_result(
    session: AsyncSession,
    origin_result: OriginResult
) -> OriginResult:
    try:
        db_origin_result: OriginResult = await db_get_origin_result(
            session= session,
            origin_result= origin_result
        )
        my_logger.debug(
            f'OriginResult({db_origin_result.origin}, {db_origin_result.inspection_result}) already created.'
        )
        return db_origin_result
    except HTTPException:
        ...
    session.add(origin_result)
    await session.commit()
    await session.refresh(origin_result)
    my_logger.debug(
        f'OriginResult({origin_result.origin}, {origin_result.inspection_result}) created.',
        Styles.SUCCEED
    )
    return origin_result

async def db_update_origin_result(
    session: AsyncSession,
    origin_result: OriginResult
) -> OriginResult:
    db_origin_result: OriginResult = await db_get_origin_result(
        session= session,
        origin_result= origin_result
    )
    db_origin_result.inspection_result = origin_result.inspection_result
    db_origin_result.threshold = origin_result.threshold
    session.add(db_origin_result)
    await session.commit()
    await session.refresh(db_origin_result)
    return db_origin_result

async def db_delete_origin_result(
    session: AsyncSession,
    origin_result: OriginResult
) -> None:
    db_origin_result: OriginResult = await db_get_origin_result(
        session= session,
        origin_result= origin_result
    )
    await session.delete(db_origin_result)
    await session.commit()

async def db_get_origin_result(
    session: AsyncSession,
    origin_result: OriginResult
) -> OriginResult:
    try:
        return await session.get_one(
            OriginResult,
            {
                'origin': origin_result.origin,
                'inspection_result': origin_result.inspection_result
            }
        )
    except NoResultFound:
        msg: str = f'OriginResult({origin_result.origin}, {origin_result.inspection_result}) not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_origin_results(
    session: AsyncSession,
    limit: int,
    offset: int
) -> Sequence[OriginResult]:
    db_origin_results: ScalarResult[OriginResult] = await session.scalars(
        select(OriginResult)
        .offset(offset)
        .limit(limit)
    )
    db_origin_results_list: Sequence[OriginResult] = db_origin_results.all()
    if len(db_origin_results_list) == 0:
        msg: str = f'OriginResult\'s not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_origin_results_list
