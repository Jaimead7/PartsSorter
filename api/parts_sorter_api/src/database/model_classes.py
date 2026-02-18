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


from typing import Optional, Sequence

from fastapi import HTTPException, status
from pyUtils import Styles
from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import my_logger
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
            f'ModelClass("{db_model_class.model}, {db_model_class.number}") already created.'
        )
        return db_model_class
    except HTTPException:
        ...
    session.add(model_class)
    await session.commit()
    await session.refresh(model_class)
    my_logger.debug(
        f'ModelClass("{model_class.model}, {model_class.number}") created.',
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
        msg: str = f'ModelClass("{model_class.model}, {model_class.number}") not found.'
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
    statement: SelectOfScalar[ModelClass] = select(ModelClass)
    statement = statement.order_by(
        col(ModelClass.model).asc(),
        col(ModelClass.number).asc()
    )
    statement = statement.offset(offset).limit(limit)
    db_model_classes: ScalarResult[ModelClass] = await session.scalars(statement)
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
    statement: SelectOfScalar[int] = select(func.max(ModelClass.number))
    statement = statement.where(ModelClass.model == model)
    result: ScalarResult[int] = await session.scalars(statement)
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
