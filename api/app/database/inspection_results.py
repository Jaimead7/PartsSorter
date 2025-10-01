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
from sqlmodel import col, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.serverConfig import my_logger
from ..models.database import Image, InspectionResult, ModelClass, OriginResult


async def db_create_new_inspection_result(
    session: AsyncSession,
    name: str
) -> InspectionResult:
    try:
        db_inspection_result: InspectionResult = await db_get_inspection_result(
            session= session,
            inspection_result= InspectionResult(name= name)
        )
        my_logger.debug(
            f'InspectionResult("{db_inspection_result.name}") already created.'
        )
        return db_inspection_result
    except HTTPException:
        ...
    inspection_result = InspectionResult(name= name)
    session.add(inspection_result)
    await session.commit()
    await session.refresh(inspection_result)
    my_logger.debug(
        f'InspectionResult("{inspection_result.name}") created.',
        Styles.SUCCEED
    )
    return inspection_result

async def db_update_inspection_result(
    session: AsyncSession,
    inspection_result: InspectionResult
) -> InspectionResult:
    db_inspection_result: InspectionResult = await db_get_inspection_result(
        session= session,
        inspection_result= inspection_result
    )
    ...
    return db_inspection_result

async def db_delete_inspection_results(
    session: AsyncSession,
    inspection_results: list[InspectionResult]
) -> None:
    db_inspection_results: Sequence[InspectionResult] = await db_get_inspection_results(
        session= session,
        inspection_results= inspection_results,
        limit= len(inspection_results),
        offset= 0
    )
    for db_inspection_result in db_inspection_results:
        await session.delete(db_inspection_result)
    await session.commit()

async def db_get_inspection_result(
    session: AsyncSession,
    inspection_result: InspectionResult
) -> InspectionResult:
    try:
        return await session.get_one(
            InspectionResult,
            inspection_result.name
        )
    except NoResultFound:
        msg: str = f'InspectionResult("{inspection_result.name}") not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_inspection_results(
    session: AsyncSession,
    inspection_results: list[InspectionResult],
    limit: int,
    offset: int
) -> Sequence[InspectionResult]:
    if len(inspection_results) > 0:
        statement: SelectOfScalar[InspectionResult] = (
            select(InspectionResult)
            .where(
                col(InspectionResult.name).in_(
                    [
                        inspection_result.name
                        for inspection_result in inspection_results
                    ]
                )
            )
            .offset(offset)
            .limit(limit)
        )
    else:
        statement: SelectOfScalar[InspectionResult] = (
            select(InspectionResult)
            .offset(offset)
            .limit(limit)
        )
    db_inspection_results: ScalarResult[InspectionResult] = await session.scalars(statement)
    db_inspection_results_list: Sequence[InspectionResult] = db_inspection_results.all()
    if len(db_inspection_results_list) == 0:
        msg: str = f'InspectionResults not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_inspection_results_list

async def db_get_inspection_result_images(
    session: AsyncSession,
    inspection_result_name: str,
    limit: int,
    offset: int
) -> Optional[list[Image]]:
    #CHECK: Performance with big number of images as this loads all images and then slice
    db_inpection_result: InspectionResult = await db_get_inspection_result(
        session= session,
        inspection_result= InspectionResult(name= inspection_result_name)
    )
    await session.refresh(
        db_inpection_result,
        attribute_names= ['images_of_result']
    )
    if db_inpection_result.images_of_result is None:
        return None
    return db_inpection_result.images_of_result[offset:offset+limit]

async def db_get_inspection_result_model_classes(
    session: AsyncSession,
    inspection_result_name: str,
    limit: int,
    offset: int
) -> Optional[list[ModelClass]]:
    #CHECK: Performance
    db_inpection_result: InspectionResult = await db_get_inspection_result(
        session= session,
        inspection_result= InspectionResult(name= inspection_result_name)
    )
    await session.refresh(
        db_inpection_result,
        attribute_names= ['model_classes_of_result']
    )
    if db_inpection_result.model_classes_of_result is None:
        return None
    return db_inpection_result.model_classes_of_result[offset:offset+limit]

async def db_get_inspection_result_origin_results(
    session: AsyncSession,
    inspection_result_name: str,
    limit: int,
    offset: int
) -> Optional[list[OriginResult]]:
    #CHECK: Performance
    db_inpection_result: InspectionResult = await db_get_inspection_result(
        session= session,
        inspection_result= InspectionResult(name= inspection_result_name)
    )
    await session.refresh(
        db_inpection_result,
        attribute_names= ['origin_results_of_result']
    )
    if db_inpection_result.origin_results_of_result is None:
        return None
    return db_inpection_result.origin_results_of_result[offset:offset+limit]
