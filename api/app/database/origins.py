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


from typing import Optional, Sequence

from fastapi import HTTPException, status
from pyUtils import Styles
from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from ..dependencies.serverConfig import my_logger
from ..models.database import Image, Model, Origin
from .models import db_get_model


async def db_create_new_origin(
    session: AsyncSession,
    origin: Origin
) -> Origin:
    try:
        db_origin: Origin = await db_get_origin(
            session= session,
            origin= origin
        )
        my_logger.debug(
            f'Origin("{db_origin.name}") already created.'
        )
        return db_origin
    except HTTPException:
        ...
    if origin.model is not None:
        await db_get_model(
            session= session,
            model= Model(name= origin.model)
        )
    session.add(origin)
    await session.commit()
    await session.refresh(origin)
    my_logger.debug(
        f'Origin("{origin.name}") created.',
        Styles.SUCCEED
    )
    return origin

async def db_update_origin(
    session: AsyncSession,
    origin: Origin
) -> Origin:
    db_origin: Origin = await db_get_origin(
        session= session,
        origin= origin
    )
    if origin.model is not None:
        await db_get_model(
            session= session,
            model= Model(name= origin.model)
        )
    db_origin.model = origin.model
    session.add(db_origin)
    await session.commit()
    await session.refresh(db_origin)
    return db_origin

async def db_delete_origins(
    session: AsyncSession,
    origins: list[Origin]
) -> None:
    db_origins: Sequence[Origin] = await db_get_origins(
        session= session,
        origins= origins,
        limit= len(origins),
        offset= 0
    )
    for db_origin in db_origins:
        await session.delete(db_origin)
    await session.commit()

async def db_get_origin(
    session: AsyncSession,
    origin: Origin
) -> Origin:
    try:
        return await session.get_one(
            Origin,
            origin.name
        )
    except NoResultFound:
        msg: str = f'Origin("{origin.name}") not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )

async def db_get_origins(
    session: AsyncSession,
    origins: list[Origin],
    limit: int,
    offset: int
) -> Sequence[Origin]:
    if len(origins) > 0:
        statement: SelectOfScalar[Origin] = (
            select(Origin)
            .where(
                col(Origin.name).in_(
                    [
                        origin.name
                        for origin in origins
                    ]
                )
            )
            .offset(offset)
            .limit(limit)
        )
    else:
        statement: SelectOfScalar[Origin] = (
            select(Origin)
            .offset(offset)
            .limit(limit)
        )
    db_origins: ScalarResult[Origin] = await session.scalars(statement)
    db_origins_list: Sequence[Origin] = db_origins.all()
    if len(db_origins_list) == 0:
        msg: str = f'Origins not found.'
        my_logger.error(msg)
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= msg
        )
    return db_origins_list

async def db_get_origin_images(
    session: AsyncSession,
    origin_name: str,
    limit: int,
    offset: int
) -> Optional[list[Image]]:
    #CHECK: Performance with big number of images
    db_origin: Origin = await db_get_origin(
        session= session,
        origin= Origin(name= origin_name)
    )
    await session.refresh(
        db_origin,
        attribute_names= ['images_of_origin']
    )
    if db_origin.images_of_origin is None:
        return None
    return db_origin.images_of_origin[offset:offset+limit]
