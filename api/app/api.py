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


from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database.manager import initDB
from .dependencies.config import (SERVER_IP, SERVER_PORT, STATIC_PATH, TAGS,
                                  my_logger)
from .routes import (config, images, inspection_results, model_classes, models,
                     origin_results, origins, web_sockets)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await initDB()
    my_logger.info('Lifespan finished.')
    yield

app = FastAPI(
    lifespan= lifespan,
    root_path= '/api'
)
app.include_router(
    web_sockets.ws_router,
    prefix= '/ws',
    tags= [TAGS.WEB_SOCKETS]
)
app.include_router(
    config.config_router,
    prefix= '/config',
    tags= [TAGS.CONFIG]
)
app.include_router(
    images.images_router,
    prefix= '/image',
    tags= [TAGS.IMAGES]
)
app.include_router(
    inspection_results.inspection_results_router,
    prefix= '/inspection-result',
    tags= [TAGS.INSPECTION_RESULTS]
)
app.include_router(
    models.models_router,
    prefix= '/model',
    tags= [TAGS.MODELS]
)
app.include_router(
    model_classes.model_classes_router,
    prefix= '/model-class',
    tags= [TAGS.MODEL_CLASSES]
)
app.include_router(
    origins.origins_router,
    prefix= '/origin',
    tags= [TAGS.ORIGINS]
)
app.include_router(
    origin_results.origin_results_router,
    prefix= '/origin-result',
    tags= [TAGS.ORIGIN_RESULTS]
)

STATIC_PATH.mkdir(parents= True, exist_ok= True)
app.mount('/static', StaticFiles(directory= STATIC_PATH), name='static')

#TODO: fix access policity
app.add_middleware(
    CORSMiddleware,
    allow_origins= ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=SERVER_IP,
        port=SERVER_PORT
    )
