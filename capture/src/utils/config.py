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
from os import getenv
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pyUtils import ConfigFileManager, MyLogger, ProjectPathsDict
from yoloModelManager import (save_yolo_manager_logs,
                              set_yolo_manager_logging_level,
                              set_yolo_manager_logs_path)


class EnvVars(Enum):
    SOURCE_NAME = 'SOURCE_NAME'
    API_IP = 'API_IP'
    LOGGING_LVL = 'LOGGING_LVL'


# APP
MY_APP: ProjectPathsDict = ProjectPathsDict().set_app_path(Path(__file__).parents[2])
MY_APP[ProjectPathsDict.DIST_PATH] = MY_APP[ProjectPathsDict.APP_PATH] / 'dist'
MY_APP[ProjectPathsDict.CONFIG_PATH] = MY_APP[ProjectPathsDict.DIST_PATH] / 'config'
MY_APP[ProjectPathsDict.CONFIG_FILE_PATH] = MY_APP[ProjectPathsDict.CONFIG_PATH] / 'config.toml'
MY_CFG: ConfigFileManager = ConfigFileManager(MY_APP[ProjectPathsDict.CONFIG_FILE_PATH])

# LOGGING
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env(EnvVars.LOGGING_LVL.value)

my_logger = MyLogger(
    logger_name= f'CaptureApp',
    logging_level= LOGGING_LVL
)

def set_capture_app_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_yolo_manager_logs_path(new_path)

def save_capture_app_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_yolo_manager_logs(value)

def set_capture_app_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_yolo_manager_logging_level(lvl)

set_capture_app_logging_level(logging.WARNING)
set_capture_app_logs_path('captureApp.log')
set_capture_app_logging_level(LOGGING_LVL)
save_capture_app_logs(True)


# ENV VARS
load_dotenv(
    dotenv_path= MY_APP[ProjectPathsDict.DIST_PATH] / '.env',
    override= False
)
_env_aux: Optional[str] = getenv(EnvVars.SOURCE_NAME.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.SOURCE_NAME.value}" from env vars.'
    my_logger.critical(msg)
    raise ImportError(msg)
SOURCE_NAME: str = _env_aux
_env_aux: Optional[str] = getenv(EnvVars.API_IP.value, None)
if _env_aux is None:
    msg: str = f'Could not import "{EnvVars.API_IP.value}" from env vars.'
    my_logger.critical(msg)
    raise ImportError(msg)
API_IP: Optional[str] = getenv(EnvVars.SOURCE_NAME.value, None)
del(_env_aux)

# CONFIG
CAMERA: int = int(MY_CFG.camera.id)
GPIO_CHIP: str = str(MY_CFG.gpio.chip)
ACTUATOR_PIN: int = int(MY_CFG.gpio.actuator_pin)
CAMERA_SENSOR_PIN: int = int(MY_CFG.gpio.camera_sensor_pin)
ACTUATOR_SENSOR_PIN: int = int(MY_CFG.gpio.actuator_sensor_pin)
_SENSORS_DISTANCE: float = float(MY_CFG.calibration.sensors_distance)
_TAPE_SPEED: float = float(MY_CFG.calibration.tape_speed)
SENSORS_INTERVAL: float = _SENSORS_DISTANCE / _TAPE_SPEED
