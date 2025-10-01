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


from typing import Optional, Sequence

from fastapi import HTTPException, status
from pyUtils import Styles
from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from ..dependencies.serverConfig import my_logger
from ..models.database import ModelClass


async def db_create_new_model_class(
    session: AsyncSession,
    model_class: ModelClass
) -> ModelClass:
    try:
        db_model_class: ModelClass = await db_get_model_class(
            session= session,
            model_class= model_class
        )
        my_logger.debug(
            f'ModelClass("{db_model_class.model}-{db_model_class.number}") already created.'
        )
        return db_model_class
    except HTTPException:
        ...
    session.add(model_class)
    await session.commit()
    await session.refresh(model_class)
    my_logger.debug(
        f'ModelClass("{model_class.model}-{model_class.number}") created.',
        Styles.SUCCEED
    )
    return model_class

async def db_update_model_class(
    session: AsyncSession,
    model_class: ModelClass
) -> ModelClass:
    db_model_class: ModelClass = await db_get_model_class(
        session= session,
        model_class= model_class
    )
    db_model_class.inspection_result = model_class.inspection_result
    session.add(db_model_class)
    await session.commit()
    await session.refresh(db_model_class)
    return db_model_class

async def db_delete_model_class(
    session: AsyncSession,
    model_class: ModelClass
) -> None:
    db_model_class: ModelClass = await db_get_model_class(
        session= session,
        model_class= model_class
    )
    await session.delete(db_model_class)
    await session.commit()

async def db_get_model_class(
    session: AsyncSession,
    model_class: ModelClass
) -> ModelClass:
    try:
        return await session.get_one(
            ModelClass,
            {
                'model': model_class.model,
                'number': model_class.number
            }
        )
    except NoResultFound:
        msg: str = f'ModelClass("{model_class.model}-{model_class.number}") not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_model_classes(
    session: AsyncSession,
    limit: int,
    offset: int
) -> Sequence[ModelClass]:
    db_model_classes: ScalarResult[ModelClass] = await session.scalars(
        select(ModelClass)
        .offset(offset)
        .limit(limit)
    )
    db_model_classes_list: Sequence[ModelClass] = db_model_classes.all()
    if len(db_model_classes_list) == 0:
        msg: str = f'InspectionResult\'s not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_model_classes_list

async def db_get_next_model_class_number_for_model(
    session: AsyncSession,
    model: str
) -> int:
    result: ScalarResult[int] = await session.scalars(
        select(func.max(ModelClass.number))
        .where(ModelClass.model == model)
    )
    max_num: Optional[int] = result.one_or_none()
    return (max_num or -1) + 1

async def db_check_if_model_class_exists(
    session: AsyncSession,
    model_class: ModelClass
) -> bool:
    try:
        await db_get_model_class(
            session= session,
            model_class= model_class
        )
        return True
    except HTTPException:
        return False
