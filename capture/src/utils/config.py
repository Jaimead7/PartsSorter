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


class EnvVars(Enum):
    ORIGIN_NAME = 'ORIGIN_NAME'
    API_IP = 'API_IP'
    LOGGING_LVL = 'LOGGING_LVL'
    ACTUATOR_PIN = 'ACTUATOR_PIN'
    CAMERA_SENSOR_PIN = 'CAMERA_SENSOR_PIN'
    ACTUATOR_SENSOR_PIN = 'ACTUATOR_SENSOR_PIN'
    SENSORS_DISTANCE = 'SENSORS_DISTANCE'
    TAPE_SPEED = 'TAPE_SPEED'


# APP
MY_APP: ProjectPathsDict = ProjectPathsDict().set_app_path(Path(__file__).parents[2])
MY_APP[ProjectPathsDict.DIST_PATH] = MY_APP[ProjectPathsDict.APP_PATH] / 'dist'

# LOGGING
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env(EnvVars.LOGGING_LVL.value)

my_logger = MyLogger(
    logger_name= f'Capture',
    logging_level= LOGGING_LVL
)

def set_capture_app_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_pyutils_logs_path(new_path)

def save_capture_app_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_pyutils_logs(value)

def set_capture_app_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_pyutils_logging_level(lvl)

set_capture_app_logging_level(logging.WARNING)
set_capture_app_logs_path('capture.log')
set_capture_app_logging_level(LOGGING_LVL)
save_capture_app_logs(True)


# ENV VARS
_env_aux: Optional[str] = getenv(EnvVars.ORIGIN_NAME.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.ORIGIN_NAME.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
ORIGIN_NAME: str = _env_aux
_env_aux: Optional[str] = getenv(EnvVars.API_IP.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.API_IP.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
API_IP: Optional[str] = getenv(EnvVars.API_IP.value, None)
del(_env_aux)

# CONFIG
CAMERA_INDEX: int = 0
GPIO_CHIP: str = '/dev/gpiochip4'
_env_aux: Optional[str] = getenv(EnvVars.ACTUATOR_PIN.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.ACTUATOR_PIN.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
ACTUATOR_PIN: int = int(_env_aux)
_env_aux: Optional[str] = getenv(EnvVars.CAMERA_SENSOR_PIN.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.CAMERA_SENSOR_PIN.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
CAMERA_SENSOR_PIN: int = int(_env_aux)
_env_aux: Optional[str] = getenv(EnvVars.ACTUATOR_SENSOR_PIN.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.ACTUATOR_SENSOR_PIN.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
ACTUATOR_SENSOR_PIN: int = int(_env_aux)
#TODO: change to variables readed from api
_env_aux: Optional[str] = getenv(EnvVars.SENSORS_DISTANCE.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.SENSORS_DISTANCE.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
_SENSORS_DISTANCE: float = float(_env_aux)
_env_aux: Optional[str] = getenv(EnvVars.TAPE_SPEED.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.TAPE_SPEED.value}" from env vars.'
    my_logger.critical(f'ImportError: {msg}')
    raise ImportError(msg)
_TAPE_SPEED: float = float(_env_aux)

SENSORS_INTERVAL_MS: float = (_SENSORS_DISTANCE / _TAPE_SPEED)*1000
