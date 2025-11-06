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


from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence, Tuple

import aiofiles
from fastapi import HTTPException, UploadFile, status
from pyUtils import ImageFileValidator, Styles
from sqlalchemy import Result, ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.config import my_logger
from ..dependencies.exceptions import StopBlock
from ..dependencies.web_sockets import ImageStreamSocketManager
from ..engine.inspection import ModelsManager
from ..models.api import ImageHistResponse
from ..models.database import (Image, ImageProcessed, InspectionResult, Origin,
                               OriginResult)
from .inspection_results import db_get_inspection_result
from .models import db_get_model_inspection_result
from .origin_results import db_get_origin_result
from .origins import db_get_origin


async def _db_add_image(
    session: AsyncSession,
    image: Image
) -> Image:
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image

async def db_create_new_image(
    session: AsyncSession,
    file: UploadFile,
    origin: Optional[str] = None
) -> Image:
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
    try:
        if origin is not None:
            await db_get_origin(
                session= session,
                origin= Origin(
                    name= origin
                )
            )
    except HTTPException:
        my_logger.warning(f'"{origin}" is not a valid Origin. Origin set to NULL.')
        origin = None
    image: Image = Image(extension= file_ext, origin= origin)
    await db_save_image(
        image= image,
        file= file
    )
    db_image: Image = await _db_add_image(
        session= session,
        image= image
    )
    return db_image

async def db_update_image(
    session: AsyncSession,
    image: Image,
) -> Image:
    db_image: Image = await db_get_image_by_id(
        session= session,
        image= image
    )
    try:
        if image.inspection_result is not None:
            await db_get_inspection_result(
                session= session,
                inspection_result= InspectionResult(
                    name= image.inspection_result
                )
            )
        db_image.inspection_result = image.inspection_result
    except HTTPException:
        my_logger.warning(f'"{image.inspection_result}" not updated.')
    try:
        if image.origin is not None:
            await db_get_origin(
                session= session,
                origin= Origin(
                    name= image.origin
                )
            )
        db_image.origin = image.origin
    except HTTPException:
        my_logger.warning(f'"{image.origin}" not updated.')
    try:
        if image.true_result is not None:
            await db_get_inspection_result(
                session= session,
                inspection_result= InspectionResult(
                    name= image.true_result
                )
            )
        db_image.true_result = image.true_result
    except HTTPException:
        my_logger.warning(f'"{image.true_result}" not updated.')
    db_image.trust = image.trust
    db_image.processed_date = datetime.now(timezone.utc).replace(tzinfo=None)
    return await _db_add_image(
        session= session,
        image= db_image
    )

async def db_delete_images(
    session: AsyncSession,
    images: list[Image]
) -> None:
    db_images: Sequence[Image] = await db_get_images_by_ids(
        session= session,
        images= images,
        limit= len(images),
        offset= 0
    )
    for db_image in db_images:
        await session.delete(db_image)
    await session.commit()

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
    images: list[Image],
    limit: int,
    offset: int
) -> Sequence[Image]:
    statement: SelectOfScalar[Image] = select(Image)
    if len(images) > 0:
        statement = statement.where(
            col(Image.id).in_([img.id for img in images])
        )
    statement = statement.offset(offset).limit(limit)
    db_images: ScalarResult[Image] = await session.scalars(statement)
    db_images_list: Sequence[Image] = db_images.all()
    if len(db_images_list) == 0:
        msg: str = f'Images not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_images_list

async def db_save_image(
    image: Image,
    file: UploadFile
) -> Image:
    async with aiofiles.open(image.internal_absolute_path, 'wb') as f:
        await f.write(await file.read())
    my_logger.debug(
        f'Image file "{image.internal_absolute_path}" saved.',
        Styles.SUCCEED
    )
    return image

def db_delete_image_file(
    image: Image
) -> Path:
    file_path: Path = image.internal_absolute_path
    if file_path.is_file():
        file_path.unlink()
    return file_path

async def db_process_new_image(
    session: AsyncSession,
    file: UploadFile,
    origin_name: Optional[str]
) -> ImageProcessed:
    db_image: Image = await db_create_new_image(
        session= session,
        file= file,
        origin= origin_name
    )
    try:
        if origin_name is None:
            raise StopBlock
        db_origin: Optional[Origin] = await db_get_origin(
            session= session,
            origin= Origin(name= origin_name)
        )
        if db_origin is None:
            raise StopBlock
        if db_origin.model is None:
            raise StopBlock
        result: Optional[int]
        trust: Optional[float]
        result, trust = await ModelsManager.inspect(
            db_image= db_image,
            model_name= db_origin.model
        )
        if result is None:
            raise StopBlock
        try:
            inpection_result: Optional[InspectionResult] = await db_get_model_inspection_result(
                session= session,
                model_name= db_origin.model,
                result= result
            )
        except HTTPException:
            raise StopBlock
        if inpection_result is None:
            raise StopBlock
        db_image.inspection_result = inpection_result.name
        db_image.trust = trust
        db_image.model = db_origin.model
        db_image.processed_date = datetime.now(timezone.utc).replace(tzinfo=None)
        db_image = await _db_add_image(
            session= session,
            image= db_image
        )
    except StopBlock:
        pass
    image_processed: ImageProcessed = ImageProcessed.factory(image= db_image)
    image_processed.result = False
    if db_image.origin is not None and db_image.inspection_result is not None:
        try:
            db_origin_result: OriginResult = await db_get_origin_result(
                session= session,
                origin_result= OriginResult(
                    origin= db_image.origin,
                    inspection_result= db_image.inspection_result
                )
            )
            image_processed.result = db_origin_result.result
            if db_image.trust is not None and db_origin_result.threshold >= db_image.trust:
                image_processed.result = True
        except HTTPException:
            pass
    await ImageStreamSocketManager.broadcast_new_result(
        image_url= db_image.external_url,
        insp_result= db_image.inspection_result,
        origin= db_image.origin,
        model= db_image.model,
        true_result= db_image.true_result,
        trust= db_image.trust
    )
    return image_processed

async def db_get_next_hist_image(
    session: AsyncSession,
    extensions: list[str],
    start_date: datetime,
    end_date: datetime,
    inspection_results: list[str],
    origins: list[str],
    models: list[str],
    true_results: list[str],
    min_trust: float,
    max_trust: float,
    index: int
) -> ImageHistResponse:
    total_images: int = await db_get_count_images_with_filters(
        session= session,
        extensions= extensions,
        start_date= start_date,
        end_date= end_date,
        inspection_results= inspection_results,
        origins= origins,
        models= models,
        true_results= true_results,
        min_trust= min_trust,
        max_trust= max_trust
    )
    db_images: Sequence[Image] = await db_get_images_with_filters(
        session= session,
        extensions= extensions,
        start_date= start_date,
        end_date= end_date,
        inspection_results= inspection_results,
        origins= origins,
        models= models,
        true_results= true_results,
        min_trust= min_trust,
        max_trust= max_trust,
        offset= index,
        limit= 1
    )
    if len(db_images) == 0:
        msg: str = f'Image not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return ImageHistResponse.factory(
        image_url= db_images[0].external_url,
        insp_result= db_images[0].inspection_result,
        origin= db_images[0].origin,
        model= db_images[0].model,
        true_result= db_images[0].true_result,
        trust= db_images[0].trust,
        index= index,
        total= total_images
    )

async def db_get_count_images_with_filters(
    session: AsyncSession,
    extensions: list[str],
    start_date: datetime,
    end_date: datetime,
    inspection_results: list[str],
    origins: list[str],
    models: list[str],
    true_results: list[str],
    min_trust: float,
    max_trust: float
) -> int:
    statement: SelectOfScalar[int] = (
        select(func.count(col(Image.id)))
        .where(
            col(Image.processed_date).is_not(None),
            col(Image.processed_date) >= start_date,
            col(Image.processed_date) <= end_date,
            col(Image.trust).is_not(None),
            col(Image.trust) >= min_trust,
            col(Image.trust) <= max_trust
        )
    )
    if len(extensions) > 0:
        statement = statement.where(
            col(Image.extension).in_(extensions)
        )
    if len(inspection_results) > 0:
        statement = statement.where(
            col(Image.inspection_result).in_(inspection_results)
        )
    if len(origins) > 0:
        statement = statement.where(
            col(Image.origin).in_(origins)
        )
    if len(models) > 0:
        statement = statement.where(
            col(Image.model).in_(models)
        )
    if len(true_results) > 0:
        statement = statement.where(
            col(Image.true_result).in_(true_results)
        )
    result: Result[Tuple[int]] = await session.execute(statement)
    return result.scalar_one()

async def db_get_images_with_filters(
    session: AsyncSession,
    extensions: list[str],
    start_date: datetime,
    end_date: datetime,
    inspection_results: list[str],
    origins: list[str],
    models: list[str],
    true_results: list[str],
    min_trust: float,
    max_trust: float,
    offset: int,
    limit: int
) -> Sequence[Image]:
    statement: SelectOfScalar[Image] = (
        select(Image)
        .where(
            col(Image.processed_date).is_not(None),
            col(Image.processed_date) >= start_date,
            col(Image.processed_date) <= end_date,
            col(Image.trust).is_not(None),
            col(Image.trust) >= min_trust,
            col(Image.trust) <= max_trust
        )
    )
    if len(extensions) > 0:
        statement = statement.where(
            col(Image.extension).in_(extensions)
        )
    if len(inspection_results) > 0:
        statement = statement.where(
            col(Image.inspection_result).in_(inspection_results)
        )
    if len(origins) > 0:
        statement = statement.where(
            col(Image.origin).in_(origins)
        )
    if len(models) > 0:
        statement = statement.where(
            col(Image.model).in_(models)
        )
    if len(true_results) > 0:
        statement = statement.where(
            col(Image.true_result).in_(true_results)
        )
    statement = statement.offset(offset).limit(limit)
    db_images: ScalarResult[Image] = await session.scalars(statement)
    return db_images.all()
