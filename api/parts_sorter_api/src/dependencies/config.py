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


import logging
from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional

from pyUtils import (MyLogger, ProjectPathsDict, save_pyutils_logs,
                     set_pyutils_logging_level, set_pyutils_logs_path)


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
