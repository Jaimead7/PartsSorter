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


import asyncio
from datetime import datetime, timezone
from pathlib import Path
from types import CoroutineType
from typing import Any, Optional, Sequence, Tuple
from uuid import UUID

import aiofiles
from fastapi import HTTPException, UploadFile, status
from pyUtils import ImageFileValidator, Styles
from sqlalchemy import Delete, Result, ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, delete, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import INTERNAL_MODELS_FOLDER, my_logger
from ..dependencies.web_sockets import ImageStreamSocketManager
from ..engine.managers import ModelManager, ModelsContainer
from ..engine.results import ResutlsType, extract_first_result
from ..engine.results_sorters import apply_results_sorters
from ..models.api import ImageFilters, ImageHistResponse, ProcessImageResult
from ..models.database import (Image, ImageProcessed, InspectionResult,
                               OriginResult)
from .inspection_results import db_inspection_result_name_exists
from .models import db_get_model_inspection_result
from .origin_results import db_get_origin_result
from .origins import db_origin_name_exists


async def _db_add_image_and_commit(
    session: AsyncSession,
    image: Image
) -> Image:
    session.add(image)
    await session.commit()
    await session.refresh(image)
    my_logger.debug(f'Image commited to the database {image.file_name}.')
    return image

async def _db_validate_upload_file_name(
    file: UploadFile
) -> str:
    if file.filename is None:
        msg: str = f'File does not have a name.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= msg
        )
    if ImageFileValidator.VALID_EXTENSIONS is None:
        valid_extensions: list[str] = []
    else:
        valid_extensions = ImageFileValidator.VALID_EXTENSIONS
    file_ext: str = Path(file.filename).suffix
    if not file_ext in valid_extensions:
        msg: str = f'File extension "{file_ext}" is not a valid extension.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= msg
        )
    my_logger.debug(f'{file.filename} validated.', Styles.SUCCEED)
    return file.filename

async def db_create_new_image(
    session: AsyncSession,
    file: UploadFile,
    origin_name: Optional[str] = None
) -> Image:
    file_name: str = await _db_validate_upload_file_name(file)
    origin_name = await db_origin_name_exists(
        session= session,
        origin_name= origin_name
    )
    image: Image = Image(
        extension= Path(file_name).suffix,
        origin= origin_name
    )
    await db_save_image_file(
        image= image,
        file= file
    )
    db_image: Image = await _db_add_image_and_commit(
        session= session,
        image= image
    )
    my_logger.info(
        f'New image added to the database ({db_image.file_name}).',
        Styles.SUCCEED
    )
    return db_image

async def db_update_image(
    session: AsyncSession,
    image: Image,
    update_date: bool = True
) -> Image:
    db_image: Image = await db_get_image_by_id(
        session= session,
        image= image
    )
    db_image.inspection_result = await db_inspection_result_name_exists(
        session= session,
        inspection_result_name= image.inspection_result
    )
    db_image.origin = await db_origin_name_exists(
        session= session,
        origin_name= image.origin
    )
    db_image.true_result = await db_inspection_result_name_exists(
        session= session,
        inspection_result_name= image.true_result
    )
    db_image.trust = image.trust
    db_image.status = image.status
    if update_date:
        db_image.processed_date = datetime.now(timezone.utc).replace(tzinfo=None)
    db_image = await _db_add_image_and_commit(
        session= session,
        image= db_image
    )
    my_logger.info(
        f'Image updated {db_image}.',
        style= Styles.SUCCEED
    )
    return db_image

async def db_delete_images_by_id(
    session: AsyncSession,
    images_uuids: list[UUID]
) -> None:
    # Files are deleted by event after_delete
    db_images: Sequence[Image] = await db_get_images_by_ids(
        session= session,
        images_uuids= images_uuids,
        limit= len(images_uuids),
        offset= 0
    )
    tasks: list[CoroutineType[Any, Any, Path]] = [
        db_delete_image_file(db_image)
        for db_image in db_images
    ]
    await asyncio.gather(*tasks)
    statement: Delete = (
        delete(Image)
        .where(col(Image.id).in_(images_uuids))
    )
    await session.execute(statement)
    await session.commit()
    my_logger.info(f'Deleted images {images_uuids}.')

async def db_get_image_by_id(
    session: AsyncSession,
    image: Image
) -> Image:
    try:
        return await session.get_one(
            Image,
            image.id
        )
    except NoResultFound:
        msg: str = f'Image("{image.id}") not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_images_by_ids(
    session: AsyncSession,
    images_uuids: list[UUID],
    limit: int,
    offset: int
) -> Sequence[Image]:
    statement: SelectOfScalar[Image] = select(Image)
    if len(images_uuids) > 0:
        statement = statement.where(
            col(Image.id).in_(images_uuids)
        )
    statement = statement.order_by(col(Image.processed_date).asc())
    statement = statement.offset(offset).limit(limit)
    db_images: Sequence[Image] = (await session.scalars(statement)).all()
    if len(db_images) == 0:
        msg: str = f'Images not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    my_logger.info(f'{len(db_images)} Images readed form database.')
    return db_images

async def db_save_image_file(
    image: Image,
    file: UploadFile
) -> Image:
    async with aiofiles.open(image.internal_absolute_path, 'wb') as f:
        await f.write(await file.read())
    my_logger.info(
        f'Image file "{image.internal_absolute_path}" saved.',
        Styles.SUCCEED
    )
    return image

async def db_delete_image_file(
    image: Image
) -> Path:
    file_path: Path = image.internal_absolute_path
    if file_path.is_file():
        file_path.unlink()
    my_logger.info(f'Image "{image.file_name}" deleted.')
    return file_path

async def db_process_image(
    session: AsyncSession,
    db_image: Image,
    model_name: Optional[str] = None
) -> ProcessImageResult:
    if model_name is None:
        await session.refresh(
            db_image,
            attribute_names= ['origin_of_image']
        )
        if db_image.origin_of_image is None or db_image.origin_of_image.model is None:
            my_logger.error(f'No model selected to process image.')
            return ProcessImageResult(
                model_name= None,
                inpection_result_name= None,
                trust= None
            )
        model_name = db_image.origin_of_image.model
    try:
        model_manager: ModelManager = ModelsContainer.get_model(INTERNAL_MODELS_FOLDER / model_name)
    except KeyError:
        my_logger.error(f'No model available to process image.')
        return ProcessImageResult(
            model_name= None,
            inpection_result_name= None,
            trust= None
        )
    results_list: list[ResutlsType] = model_manager.inspect(db_image.internal_absolute_path)
    if len(results_list) < 1:
        my_logger.error(f'Error processing image.')
        return ProcessImageResult(
            model_name= model_name,
            inpection_result_name= None,
            trust= None
        )
    results: ResutlsType = results_list[0]
    results = apply_results_sorters(
        results= results,
        sorters= ('center',)  #TODO: use sorters by origin
    )
    result_id: Optional[int]
    trust: Optional[float]
    result_id, trust = extract_first_result(results)
    my_logger.info(f'Image "{db_image.file_name}" processed with Model "{model_name}".')
    if result_id is None or trust is None:
        return ProcessImageResult(
                model_name= model_name,
                inpection_result_name= None,
                trust= None
            )
    try:
        inpection_result: InspectionResult = await db_get_model_inspection_result(
            session= session,
            model_name= model_name,
            result_id= result_id
        )
    except HTTPException:
        return ProcessImageResult(
                model_name= model_name,
                inpection_result_name= None,
                trust= None
            )
    return ProcessImageResult(
        model_name= model_name,
        inpection_result_name= inpection_result.name,
        trust= trust
    )

async def db_get_image_origin_result(
    session: AsyncSession,
    image: Image
) -> bool:
    if image.origin is None or image.inspection_result is None or image.trust is None:
        return True
    try:
        db_origin_result: OriginResult = await db_get_origin_result(
            session= session,
            origin_result= OriginResult(
                origin= image.origin,
                inspection_result= image.inspection_result
            )
        )
        if db_origin_result.threshold >= image.trust:
            return True
        return db_origin_result.result
    except HTTPException:
        pass
    return True

async def db_create_and_process_new_image(
    session: AsyncSession,
    file: UploadFile,
    origin_name: Optional[str]
) -> ImageProcessed:
    db_image: Image = await db_create_new_image(
        session= session,
        file= file,
        origin_name= origin_name
    )
    process_image_result: ProcessImageResult = await db_process_image(
        session= session,
        db_image= db_image,
    )
    db_image.inspection_result = process_image_result.inpection_result_name
    db_image.trust = process_image_result.trust
    db_image.model = process_image_result.model_name
    db_image.processed_date = datetime.now(timezone.utc).replace(tzinfo=None)
    db_image = await _db_add_image_and_commit(
        session= session,
        image= db_image
    )
    image_processed: ImageProcessed = ImageProcessed.factory(image= db_image)
    image_processed.result = await db_get_image_origin_result(
        session= session,
        image= db_image
    )
    await ImageStreamSocketManager.broadcast_new_result(db_image)
    return image_processed

async def db_get_next_hist_image(
    session: AsyncSession,
    filters: ImageFilters,
    index: int
) -> ImageHistResponse:
    total_images: int = await db_get_count_images_with_filters(
        session= session,
        filters= filters
    )
    if total_images == 0:
        msg: str = f'Images not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    if index > total_images - 1:
        index = total_images - 1
    if index < 0:
        index = 0
    db_images: Sequence[Image] = await db_get_images_with_filters(
        session= session,
        filters= filters,
        offset= index,
        limit= 1
    )
    if len(db_images) == 0:
        msg: str = f'Images not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return ImageHistResponse.from_image(
        image= db_images[0],
        index= index,
        total= total_images
    )

async def db_get_count_images_with_filters(
    session: AsyncSession,
    filters: ImageFilters
) -> int:
    statement: SelectOfScalar[int] = select(func.count(col(Image.id)))
    statement = filters.add_filters_to_statement(statement)
    result: Result[Tuple[int]] = await session.execute(statement)
    return result.scalar_one()

async def db_get_images_with_filters(
    session: AsyncSession,
    filters: ImageFilters,
    offset: int,
    limit: int
) -> Sequence[Image]:
    statement: SelectOfScalar[Image] = select(Image)
    statement = filters.add_filters_to_statement(statement)
    statement = statement.order_by(col(Image.processed_date).asc())
    statement = statement.offset(offset).limit(limit)
    db_images: ScalarResult[Image] = await session.scalars(statement)
    return db_images.all()

async def db_get_image_extensions(
    session: AsyncSession
) -> Sequence[str]:
    statement: SelectOfScalar[str] = select(Image.extension).distinct()
    result: ScalarResult[str] = await session.scalars(statement)
    return result.all()
