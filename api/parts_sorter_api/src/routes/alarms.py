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
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.alarms import (db_create_new_alarm, db_delete_alarm_by_id,
                               db_get_alarms_page)
from ..database.manager import get_session
from ..dependencies.config import DATABASE_GET_LIMIT
from ..dependencies.web_sockets import ImageStreamSocketManager
from ..models.api import AlarmFilters, AlarmResponse, AlarmsListResponse
from ..models.database import Alarm, AlarmTypes

alarms_router: APIRouter = APIRouter()

@alarms_router.post(
    '/',
    response_model= AlarmResponse,
    summary= 'Post a new alarm.',
    response_description= 'The new Alarm created.',
    status_code= status.HTTP_201_CREATED
)
async def new_alarm(
    session: Annotated[AsyncSession, Depends(get_session)],
    bg_tasks: BackgroundTasks,
    alarm: Annotated[Alarm, Body()],
) -> AlarmResponse:
    db_alarm: Alarm = await db_create_new_alarm(
        session= session,
        alarm= alarm
    )
    response: AlarmResponse = AlarmResponse.from_alarm(db_alarm)
    bg_tasks.add_task(
        ImageStreamSocketManager.broadcast,
        response
    )
    return response

@alarms_router.get(
    '/',
    response_model= AlarmsListResponse,
    summary= 'Get Alarm\'s of the database.',
    response_description= 'The Alarm\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_alarms(
    session: Annotated[AsyncSession, Depends(get_session)],
    start_date: Annotated[Optional[datetime], Query()] = None,
    end_date: Annotated[Optional[datetime], Query()] = None,
    origin: Annotated[list[Optional[str]], Query()] = [],
    alarm_type: Annotated[list[str | int], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    page: Annotated[int, Query()] = 0
) -> AlarmsListResponse:
    filters: AlarmFilters = AlarmFilters(
        start_date= start_date,
        end_date= end_date,
        origins= origin,
        alarm_types= alarm_type
    )
    db_alarms: Sequence[Alarm]
    current_page: int
    total_pages: int
    db_alarms, current_page, total_pages = await db_get_alarms_page(
        session= session,
        filters= filters,
        limit= limit,
        page= page
    )
    list_response = AlarmsListResponse(
        alarms= [AlarmResponse.from_alarm(alarm= alarm) for alarm in db_alarms],
        current_page= current_page,
        total_pages= total_pages
    )
    return list_response

@alarms_router.delete(
    '/',
    summary= 'Delete Alarm\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_alarms(
    session: Annotated[AsyncSession, Depends(get_session)],
    uuids: Annotated[list[UUID], Body(embed= True)]
) -> None:
    await db_delete_alarm_by_id(
        session= session,
        alarms_uuids= uuids
    )

@alarms_router.get(
    '/types/',
    response_model= list[str],
    summary= 'Get all available types for the Alarms.',
    response_description= 'The alarm types list.',
    status_code= status.HTTP_200_OK
)
async def get_alarm_types() -> Sequence[str]:
    return AlarmTypes.get_all_names()
