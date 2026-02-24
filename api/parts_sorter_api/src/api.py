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


from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database.manager import initDB
from .dependencies.config import (SERVER_IP, SERVER_PORT, STATIC_PATH, TAGS,
                                  my_logger)
from .routes import (alarms, config, images, inspection_results, model_classes,
                     models, origin_results, origins, web_sockets)


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
app.include_router(
    alarms.alarms_router,
    prefix= '/alarm',
    tags= [TAGS.ALARMS]
)

STATIC_PATH.mkdir(parents= True, exist_ok= True)
app.mount('/static', StaticFiles(directory= STATIC_PATH), name='static')

#TODO: Change policity to only acept connections from nginx
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
        host= SERVER_IP,
        port= SERVER_PORT
    )
