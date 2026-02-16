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


from typing import Annotated, Optional, Sequence

from fastapi import APIRouter, Body, Depends, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.models import (db_create_new_model, db_delete_models,
                               db_get_model, db_get_model_metadata,
                               db_get_model_model_classes,
                               db_get_model_origins, db_get_models,
                               db_update_model)
from ..dependencies.config import DATABASE_GET_LIMIT
from ..models.database import Model, ModelClass, Origin
from ..models.metadata_files import ModelMetadataDict

models_router = APIRouter()

@models_router.post(
    '/',
    response_model= Model,
    summary= 'Create new Model on the database.',
    response_description= 'The new Model created.',
    status_code= status.HTTP_201_CREATED
)
async def create_new_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    file: UploadFile
) -> Model:
    return await db_create_new_model(
        session= session,
        file= file
    )

@models_router.get(
    '/',
    response_model= list[Model],
    summary= 'Get Model\'s of the database.',
    response_description= 'The Model\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_models(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: Annotated[list[str], Query()] = [],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> Sequence[Model]:
    return await db_get_models(
        session= session,
        models= [Model(name= name) for name in names],
        limit= limit,
        offset= offset
    )

@models_router.delete(
    '/',
    summary= 'Delete Model\'s from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_models(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: Annotated[list[str], Body(embed= True)]
) -> None:
    models: list[Model] = [Model(name= name) for name in names]
    await db_delete_models(
        session= session,
        models= models
    )

@models_router.get(
    '/{name}/',
    response_model= Model,
    summary= 'Get Model of the database.',
    response_description= 'The Model list.',
    status_code= status.HTTP_200_OK
)
async def get_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> Model:
    return await db_get_model(
        session= session,
        model= Model(name= name)
    )

@models_router.delete(
    '/{name}/',
    summary= 'Delete Model from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> None:
    await db_delete_models(
        session= session,
        models= [Model(name= name)]
    )

@models_router.put(
    '/{name}/',
    response_model= Model,
    summary= 'Update Model on the database.',
    response_description= 'The Model updated.',
    status_code= status.HTTP_200_OK
)
async def update_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> Model:
    return await db_update_model(
        session= session,
        model= Model(name= name)
    )

@models_router.get(
    '/{name}/model-classes/',
    response_model= list[ModelClass],
    summary= 'Get the ModelClass\'s of a Model of the database.',
    response_description= 'The ModelClass\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_model_model_classes(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> Optional[list[ModelClass]]:
    return await db_get_model_model_classes(
        session= session,
        model_name= name
    )

@models_router.get(
    '/{name}/origins/',
    response_model= list[Origin],
    summary= 'Get the Origin\'s of a Model of the database.',
    response_description= 'The Origin\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_model_origins(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()],
    limit: Annotated[int, Query()] = DATABASE_GET_LIMIT,
    offset: Annotated[int, Query()] = 0
) -> list[Origin] | None:
    return await db_get_model_origins(
        session= session,
        model_name= name,
        limit= limit,
        offset= offset
    )

@models_router.get(
    '/{name}/metadata/',
    response_model= ModelMetadataDict,
    summary= 'Get the metadata of a Model.',
    response_description= 'The metadata.',
    status_code= status.HTTP_200_OK
)
async def get_model_metadata(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: Annotated[str, Path()]
) -> ModelMetadataDict:
    return await db_get_model_metadata(
        session= session,
        model_name= name
    )
