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


import asyncio
from pathlib import Path
from shutil import rmtree
from types import CoroutineType
from typing import Any, Optional, Sequence

import yaml
from fastapi import HTTPException, UploadFile, status
from pyUtils import Styles, unzip_dir
from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import my_logger
from ..models.database import InspectionResult, Model, ModelClass, Origin
from ..models.typing import ModelMetadataDict
from .inspection_results import db_create_new_inspection_result
from .model_classes import db_create_new_model_class, db_get_model_class


async def db_create_new_model(
    session: AsyncSession,
    file: UploadFile
) -> Model:
    #TODO: validate folder structure
    if file.filename is None:
        msg: str = f'File does not have a name.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= msg
        )
    if not file.filename.lower().endswith('.zip'):
        msg: str = f'File "{file.filename}" is not a ".zip" file.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= msg
        )
    safe_name: str = file.filename.replace(' ', '_').replace('.zip', '')
    model: Model = Model(name= safe_name)
    exists = False
    try:
        await db_get_model(
            session= session,
            model= model
        )
        exists = True
    except HTTPException:
        ...
    if exists:
        msg: str = f'Model("{safe_name}") already exists.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= msg
        )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    try:
        await db_save_model_zip_file(
            model= model,
            file= file
        )
        metadata_file: Path = model.internal_absolute_path / 'metadata.yaml'
        with open(metadata_file, 'r') as f:
            data: ModelMetadataDict = ModelMetadataDict(**yaml.safe_load(f))
        for number, name in data.name.items():
            inspection_result: InspectionResult = await db_create_new_inspection_result(
                session= session,
                name= name
            )
            await db_create_new_model_class(
                session= session,
                model_class= ModelClass(
                    model= model.name,
                    number= number,
                    inspection_result= inspection_result.name
                )
            )
    except:
        await db_delete_models(
            session= session,
            models= [model]
        )
        msg: str = f'Error saving model file "{file.filename}".'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= msg
        )
    my_logger.debug(
        f'Model("{model.name}") created.',
        Styles.SUCCEED
    )
    return model

async def db_update_model(
    session: AsyncSession,
    model: Model
) -> Model:
    db_model: Model = await db_get_model(
        session= session,
        model= model
    )
    ...
    return db_model

async def db_delete_models(
    session: AsyncSession,
    models: list[Model]
) -> None:
    db_models: Sequence[Model] = await db_get_models(
        session= session,
        models= models,
        limit= len(models),
        offset= 0
    )
    tasks: list[CoroutineType[Any, Any, Path]] = [
        db_delete_model_dir(db_model)
        for db_model in db_models
    ]
    await asyncio.gather(*tasks)
    for db_model in db_models:
        await session.delete(db_model)
    await session.commit()

async def db_get_model(
    session: AsyncSession,
    model: Model
) -> Model:
    try:
        return await session.get_one(
            Model,
            model.name
        )
    except NoResultFound:
        msg: str = f'Model("{model.name}") not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_models(
    session: AsyncSession,
    models: list[Model],
    limit: int,
    offset: int
) -> Sequence[Model]:
    statement: SelectOfScalar[Model] = select(Model)
    if len(models) > 0:
        statement = statement.where(
            col(Model.name).in_([model.name for model in models])
        )
    statement = statement.offset(offset).limit(limit)
    db_models: ScalarResult[Model] = await session.scalars(statement)
    db_models_list: Sequence[Model] = db_models.all()
    if len(db_models_list) == 0:
        msg: str = f'Models not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_models_list

async def db_get_model_inspection_result(
    session: AsyncSession,
    model_name: str,
    result_id: int
) -> InspectionResult:
    db_model_class: ModelClass = await db_get_model_class(
        session= session,
        model_class= ModelClass(
            model= model_name,
            number= result_id
        )
    )
    await session.refresh(
        db_model_class,
        attribute_names= ['result_of_model_class']
    )
    if db_model_class.result_of_model_class is None:
        msg: str = f'InspectionResult not found for Model({model_name}) and Id({result_id}).'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_model_class.result_of_model_class
    
async def db_save_model_zip_file(
    model: Model,
    file: UploadFile
) -> Model:
    zip_file_path: Path = model.internal_absolute_path.with_suffix('.zip')
    try:
        with open(zip_file_path, 'wb') as f:
            f.write(await file.read())
        unzip_dir(zip_file_path)
    except:
        msg: str = f'Error saving zip file.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= msg
        )
    finally:
        if zip_file_path.exists():
            zip_file_path.unlink()
    return model

async def db_get_model_model_classes(
    session: AsyncSession,
    model_name: str
) -> Optional[list[ModelClass]]:
    db_model: Model = await db_get_model(
        session= session,
        model= Model(name= model_name)
    )
    await session.refresh(
        db_model,
        attribute_names= ['model_classes_of_model']
    )
    return db_model.model_classes_of_model

async def db_get_model_origins(
    session: AsyncSession,
    model_name: str,
    limit: int,
    offset: int
) -> Optional[list[Origin]]:
    #CHECK: Performance with big number of origins
    db_model: Model = await db_get_model(
        session= session,
        model= Model(name= model_name)
    )
    await session.refresh(
        db_model,
        attribute_names= ['origins_of_model']
    )
    if db_model.origins_of_model is None:
        return None
    return db_model.origins_of_model[offset:offset+limit]

async def db_get_model_metadata(
    session: AsyncSession,
    model_name: str
) -> ModelMetadataDict:
    db_model: Model = await db_get_model(
        session= session,
        model= Model(name= model_name)
    )
    return db_model.model_metadata

async def db_delete_model_dir(
    model: Model
) -> Path:
    dir_path: Path = model.internal_absolute_path
    if dir_path.is_dir():
        rmtree(dir_path)
    return dir_path
