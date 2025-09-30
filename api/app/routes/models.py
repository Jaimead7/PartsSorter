# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmial.com>
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


from typing import Annotated, Optional, Sequence

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.manager import get_session
from ..database.models import (db_create_new_model, db_delete_models,
                               db_get_model_metadata,
                               db_get_model_model_classes,
                               db_get_model_origins, db_get_models,
                               db_update_model)
from ..dependencies.serverConfig import DATABASE_GET_LIMIT
from ..models.database import Model, ModelClass, Origin
from ..models.typing import ModelMetadataDict

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

@models_router.put(
    '/',
    response_model= Model,
    summary= 'Update Model on the database.',
    response_description= 'The Model updated.',
    status_code= status.HTTP_200_OK
)
async def update_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    model: Annotated[Model, Query()]
) -> Model:
    return await db_update_model(
        session= session,
        model= model
    )

@models_router.delete(
    '/',
    summary= 'Delete Model from the database.',
    status_code= status.HTTP_204_NO_CONTENT
)
async def delete_model(
    session: Annotated[AsyncSession, Depends(get_session)],
    names: list[str] = Query([]),
) -> None:
    models: list[Model] = [Model(name= name) for name in names]
    await db_delete_models(
        session= session,
        models= models
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
    names: list[str] = Query([]),
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> Sequence[Model]:
    return await db_get_models(
        session= session,
        models= [Model(name= name) for name in names],
        limit= limit,
        offset= offset
    )

@models_router.get(
    '/{name}/model-classes',
    response_model= list[ModelClass],
    summary= 'Get the ModelClass\'s of a Model of the database.',
    response_description= 'The ModelClass\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_model_model_classes(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str
) -> Optional[list[ModelClass]]:
    return await db_get_model_model_classes(
        session= session,
        model_name= name
    )

@models_router.get(
    '/{name}/origins',
    response_model= list[Origin],
    summary= 'Get the Origin\'s of a Model of the database.',
    response_description= 'The Origin\'s list.',
    status_code= status.HTTP_200_OK
)
async def get_model_origins(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str,
    limit: int = DATABASE_GET_LIMIT,
    offset: int = 0
) -> list[Origin] | None:
    return await db_get_model_origins(
        session= session,
        model_name= name,
        limit= limit,
        offset= offset
    )

@models_router.get(
    '/{name}/metadata',
    response_model= ModelMetadataDict,
    summary= 'Get the metadata of a Model.',
    response_description= 'The metadata.',
    status_code= status.HTTP_200_OK
)
async def get_model_metadata(
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str
) -> ModelMetadataDict:
    return await db_get_model_metadata(
        session= session,
        model_name= name
    )
