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

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.model_classes import (db_create_new_model_class,
                                      db_delete_model_class,
                                      db_get_model_classes,
                                      db_update_model_class)
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import ModelClass

model_classes_router = APIRouter()

@model_classes_router.post(
    '/',
    response_model= ModelClass,
    summary= 'Create new ModelClass on the database.',
    response_description= 'The new ModelClass created.'
)
async def create_new_model_class(
    session: Annotated[AsyncSession, Depends(get_session)],
    model_class: Annotated[ModelClass, Query()]
) -> ModelClass:
    return await db_create_new_model_class(
        session= session,
        model_class= model_class
    )

@model_classes_router.put(
    '/',
    response_model= ModelClass,
    summary= 'Update ModelClass on the database.',
    response_description= 'The ModelClass updated.',
    status_code= status.HTTP_200_OK
)
async def update_model_class(
    session: Annotated[AsyncSession, Depends(get_session)],
    model_class: Annotated[ModelClass, Query()]
) -> ModelClass:
    return await db_update_model_class(
        session= session,
        model_class= model_class
    )

@model_classes_router.delete(
    '/',
    summary= 'Delete ModelClass from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_model_class(
    session: Annotated[AsyncSession, Depends(get_session)],
    model: str,
    number: int
) -> None:
    model_class: ModelClass = ModelClass(model= model, number= number)
    await db_delete_model_class(
        session= session,
        model_class= model_class
    )

@model_classes_router.get(
    '/',
    response_model= list[ModelClass],
    summary= 'Get ModelClass\'s of the database.',
    response_description= 'The ModelClass\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_model_classes(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> Sequence[ModelClass]:
    return await db_get_model_classes(
        session= session,
        limit= limit,
        offset= offset
    )
