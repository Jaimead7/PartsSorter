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
    HOST_IP = 'HOST_IP'


# APP
MY_APP: ProjectPathsDict = ProjectPathsDict().set_app_path(Path(__file__).parents[2])
MY_APP[ProjectPathsDict.DIST_PATH] = MY_APP[ProjectPathsDict.APP_PATH] / 'dist'
MY_APP['images'] = MY_APP[ProjectPathsDict.DIST_PATH] / 'images' / 'production'
MY_APP['models'] = MY_APP[ProjectPathsDict.DIST_PATH] / 'models'


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
HOST_IP: str = getenv(EnvVars.HOST_IP.value, 'localhost')
STATIC_PATH: Path = MY_APP[ProjectPathsDict.DIST_PATH]
INTERNAL_IMAGES_FOLDER: Path = MY_APP['images']
_static_images_path: str = (Path("static") / MY_APP['images'].relative_to(MY_APP[ProjectPathsDict.DIST_PATH])).as_posix()
EXTERNAL_IMAGES_URL: str = f'http://{HOST_IP}/api/{_static_images_path}/'
INTERNAL_MODELS_FOLDER: Path = MY_APP['models']
_static_models_path: str = (Path("static") / MY_APP['models'].relative_to(MY_APP[ProjectPathsDict.DIST_PATH])).as_posix()
EXTERNAL_MODELS_URL: str = f'http://{HOST_IP}:{SERVER_PORT}/{_static_models_path}/'
DATABASE_URL: str = getenv(EnvVars.DATABASE_URL.value, 'sqlite+aiosqlite:///./database.db')
DATABASE_GET_LIMIT = int(getenv(EnvVars.DATABASE_GET_LIMIT.value, 50))
