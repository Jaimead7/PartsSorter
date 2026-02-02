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
from ..database.model_classes import (db_create_new_model_class,
                                      db_delete_model_class,
                                      db_get_model_classes,
                                      db_update_model_class)
from ..dependencies.config import DATABASE_GET_LIMIT
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
    model_class: Annotated[ModelClass, Body()]
) -> ModelClass:
    return await db_create_new_model_class(
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
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[ModelClass]:
    return await db_get_model_classes(
        session= session,
        limit= limit,
        offset= offset
    )

@model_classes_router.put(
    '/{model}/{number}/',
    response_model= ModelClass,
    summary= 'Update ModelClass on the database.',
    response_description= 'The ModelClass updated.',
    status_code= status.HTTP_200_OK
)
async def update_model_class(
    session: Annotated[AsyncSession, Depends(get_session)],
    model: Annotated[str, Path()],
    number: Annotated[int, Path()],
    inspection_result: Annotated[str, Body()]
) -> ModelClass:
    return await db_update_model_class(
        session= session,
        model_class= ModelClass(
            model= model,
            number= number,
            inspection_result= inspection_result
        )
    )

@model_classes_router.delete(
    '/{model}/{number}/',
    summary= 'Delete ModelClass from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_model_class(
    session: Annotated[AsyncSession, Depends(get_session)],
    model: Annotated[str, Path()],
    number: Annotated[int, Path()],
) -> None:
    model_class: ModelClass = ModelClass(model= model, number= number)
    await db_delete_model_class(
        session= session,
        model_class= model_class
    )
