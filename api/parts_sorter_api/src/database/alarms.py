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
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, delete, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import my_logger
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

async def db_get_alarms_by_type(
    session: AsyncSession,
    alarm_types: list[str |int],
    limit: int,
    offset:int
) -> Sequence[Alarm]:
    statement: SelectOfScalar[Alarm] = select(Alarm)
    if len(alarm_types) > 0:
        statement = statement.where(
            col(Alarm.alarm_type).in_(
                [AlarmTypes.get_value(v) for v in alarm_types]
            )
        )
    statement.order_by(col(Alarm.date).asc())
    statement = statement.offset(offset).limit(limit)
    db_alarms: Sequence[Alarm] = (await session.scalars(statement)).all()
    if len(db_alarms) == 0:
        msg: str = f'Alarms not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    my_logger.info(f'{len(db_alarms)} Alarms readed form database.')
    return db_alarms

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
