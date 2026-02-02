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


import logging
from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional

from pyUtils import (MyLogger, save_pyutils_logs, set_pyutils_logging_level,
                     set_pyutils_logs_path)


class TAGS(Enum):
    CONFIG = 'Configuration'
    WEB_SOCKETS = 'Web Sockets'
    IMAGES = 'Images'
    INSPECTION_RESULTS = 'Inspection results'
    MODEL_CLASSES = 'Model classes'
    MODELS = 'Models'
    ORIGINS = 'Origins'
    ORIGIN_RESULTS = 'Origin results'


class EnvVars(Enum):
    LOGGING_LVL = 'LOGGING_LVL'
    SERVER_IP = 'SERVER_IP'
    SERVER_PORT = 'SERVER_PORT'
    DATABASE_URL = 'DATABASE_URL'
    DATABASE_GET_LIMIT = 'DATABASE_GET_LIMIT'
    STATIC_PATH = 'STATIC_PATH'


# LOGGING
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env(EnvVars.LOGGING_LVL.value)

my_logger: MyLogger = MyLogger(
    logger_name= 'api',
    logging_level= LOGGING_LVL
)

def set_api_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_pyutils_logs_path(new_path)

def save_api_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_pyutils_logs(value)

def set_api_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_pyutils_logging_level(lvl)

set_api_logging_level(logging.WARNING)
set_api_logs_path('api.log')
set_api_logging_level(LOGGING_LVL)
save_api_logs(True)


# ENV VARS
SERVER_IP: str = getenv(EnvVars.SERVER_IP.value, 'localhost')
SERVER_PORT: int = int(getenv(EnvVars.SERVER_PORT.value, 8000))
_auxEnv: Optional[str] = getenv(EnvVars.STATIC_PATH.value, None)
if _auxEnv is None:
    _msg: str = f'{EnvVars.STATIC_PATH.value} not found in ENV VARS.'
    my_logger.critical(_msg)
    raise SystemError(_msg)
try:
    STATIC_PATH: Path = Path(_auxEnv)
except Exception as e:
    _msg = f'Unable to set {EnvVars.STATIC_PATH.value} from ENV VARS.'
    my_logger.critical(_msg)
    raise NotADirectoryError(_msg)
if not STATIC_PATH.is_dir():
    _msg = f'{STATIC_PATH} does not exists.'
    my_logger.critical(_msg)
    raise NotADirectoryError(_msg)
INTERNAL_IMAGES_FOLDER: Path = STATIC_PATH / 'images' / 'production'
if not INTERNAL_IMAGES_FOLDER.is_dir():
    _msg = f'{INTERNAL_IMAGES_FOLDER} does not exists.'
    my_logger.critical(_msg)
    raise NotADirectoryError(_msg)
STATIC_IMAGES_FOLDER: Path = Path('static') / INTERNAL_IMAGES_FOLDER.relative_to(STATIC_PATH)
INTERNAL_MODELS_FOLDER: Path = STATIC_PATH / 'models'
if not INTERNAL_MODELS_FOLDER.is_dir():
    _msg = f'{INTERNAL_MODELS_FOLDER} does not exists.'
    my_logger.critical(_msg)
    raise NotADirectoryError(_msg)
_auxEnv: Optional[str] = getenv(EnvVars.DATABASE_URL.value, None)
if _auxEnv is None:
    _msg: str = f'{EnvVars.DATABASE_URL.value} not found in ENV VARS.'
    my_logger.critical(_msg)
    raise SystemError(_msg)
DATABASE_URL: str = _auxEnv
DATABASE_GET_LIMIT = int(getenv(EnvVars.DATABASE_GET_LIMIT.value, 50))
