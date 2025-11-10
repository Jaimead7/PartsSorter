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
