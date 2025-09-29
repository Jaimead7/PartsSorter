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


from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel

from ..dependencies.serverConfig import DATABASE_URL
from ..models.database import Image, Model
from .images import db_delete_image_file
from .models import db_delete_model_dir

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo= True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    class_= AsyncSession,
    bind= engine,
    expire_on_commit= False
)

async def initDB() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSessionLocal() as session:
        ...

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@event.listens_for(Image, 'after_delete')
def event_delete_image(mapper, connection, image: Image) -> None:
    db_delete_image_file(image)

@event.listens_for(Model, 'after_delete')
def event_delete_model(mapper, connection, model: Model) -> None:
    db_delete_model_dir(model)
