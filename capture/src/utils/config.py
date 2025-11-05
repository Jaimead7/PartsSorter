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
