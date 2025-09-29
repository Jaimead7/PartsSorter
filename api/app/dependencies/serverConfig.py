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


import logging
from enum import Enum
from pathlib import Path

from pyUtils import (MyLogger, save_pyutils_logs, set_pyutils_logging_level,
                     set_pyutils_logs_path)

#TODO: change to .env
SERVER_IP = "localhost" #TODO: Change to server ip
SERVER_PORT = 8000
SERVER_URL: str = f'http://{SERVER_IP}:{SERVER_PORT}/'
INTERNAL_IMAGES_FOLDER: Path = Path(__file__).parents[1] / 'static' / 'images'
EXTERNAL_IMAGES_URL: str = SERVER_URL + (Path('static') / 'images').as_posix() + '/'
INTERNAL_MODELS_FOLDER: Path = Path(__file__).parents[1] / 'static' / 'models'
EXTERNAL_MODELS_URL: str = SERVER_URL + (Path('static') / 'models').as_posix() + '/'
DATABASE_URL = 'sqlite+aiosqlite:///./database.db' #TODO: Change database url
DATABASE_GET_LIMIT = 50
LOGGING_LVL = logging.DEBUG


class TAGS(Enum):
    WEB_SOCKETS = 'Web Sockets'
    IMAGES = 'Images'
    INSPECTION_RESULTS = 'Inspection results'
    MODEL_CLASSES = 'Model classes'
    MODELS = 'Models'
    ORIGINS = 'Origins'


my_logger: MyLogger = MyLogger(
    logger_name= 'WebServer',
    logging_level= LOGGING_LVL
)

def set_web_server_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_pyutils_logs_path(new_path)

def save_web_server_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_pyutils_logs(value)

def set_web_server_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_pyutils_logging_level(lvl)

set_web_server_logging_level(logging.WARNING)
set_web_server_logs_path('webServer.log')
set_web_server_logging_level(LOGGING_LVL)
save_web_server_logs(True)
