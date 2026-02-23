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
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Delete, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, delete, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import my_logger
from ..models.api import AlarmFilters
from ..models.database import Alarm, AlarmTypes
from .origins import db_origin_name_exists


async def db_create_new_alarm(
    session: AsyncSession,
    alarm: Alarm
) -> Alarm:
    alarm.origin = await db_origin_name_exists(
        session= session,
        origin_name= alarm.origin
    )
    session.add(alarm)
    await session.commit()
    await session.refresh(alarm)
    my_logger.debug(f'New alarm added to the database {alarm.id}.')
    return alarm

async def db_get_alarms_page(
    session: AsyncSession,
    filters: AlarmFilters,
    limit: int,
    page: int
) -> tuple[Sequence[Alarm], int, int]:
    current_page: int
    total_pages: int
    current_page, total_pages = await _db_get_pagination(
        session= session,
        filters= filters,
        limit= limit,
        page= page
    )
    db_alarms: Sequence[Alarm] = await _db_get_alarms(
        session= session,
        filters= filters,
        limit= limit,
        page= current_page
    )
    if len(db_alarms) == 0:
        msg: str = f'Alarms not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    my_logger.info(f'{len(db_alarms)} Alarms readed form database.')
    return db_alarms, current_page, total_pages

async def _db_get_alarms(
    session: AsyncSession,
    filters: AlarmFilters,
    limit: int,
    page: int
) -> Sequence[Alarm]:
    statement: SelectOfScalar[Alarm] = select(Alarm)
    statement = filters.add_filters_to_statement(statement)
    statement.order_by(col(Alarm.date).asc())
    statement = statement.offset(page * limit).limit(limit)
    return (await session.scalars(statement)).all()

async def _db_get_pagination(
    session: AsyncSession,
    filters: AlarmFilters,
    limit: int,
    page: int
) -> tuple[int, int]:
    total_alarms: int = await db_get_total_alarms(
        session= session,
        filters= filters
    )
    if total_alarms == 0:
        return 0, 0
    total_pages: int = ceil(total_alarms / limit)
    page = min(page, total_pages)
    return page, total_pages

async def db_get_total_alarms(
    session: AsyncSession,
    filters: AlarmFilters,
) -> int:
    statement: SelectOfScalar[int] = select(func.count(col(Alarm.id)))
    statement = filters.add_filters_to_statement(statement)
    result: Result[tuple[int]] = await session.execute(statement)
    return result.scalar_one()

async def db_delete_alarm_by_id(
    session: AsyncSession,
    alarms_uuids: list[UUID]
) -> None:
    statement: Delete = (
        delete(Alarm)
        .where(col(Alarm.id).in_(alarms_uuids))
    )
    await session.execute(statement)
    await session.commit()
    my_logger.info(f'Deleted images {alarms_uuids}.')
