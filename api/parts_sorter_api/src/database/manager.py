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
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel

from ..dependencies.config import DATABASE_URL
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
    try:
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(db_delete_image_file(image))
            return
    except RuntimeError:
        pass
    asyncio.run(db_delete_image_file(image))    

@event.listens_for(Model, 'after_delete')
def event_delete_model(mapper, connection, model: Model) -> None:
    try:
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(db_delete_model_dir(model))
            return
    except RuntimeError:
        pass
    asyncio.run(db_delete_model_dir(model))
