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
    LOGGING_LVL = 'LOGGING_LVL'
    CAMERA = 'CAMERA'
    GPIO_CHIP = 'GPIO_CHIP'
    ACTUATOR_PIN = 'ACTUATOR_PIN'
    CAMERA_SENSOR_PIN = 'CAMERA_SENSOR_PIN'
    ACTUATOR_SENSOR_PIN = 'ACTUATOR_SENSOR_PIN'
    SENSORS_INTERVAL = 'SENSORS_INTERVAL'


_MY_APP: ProjectPathsDict = ProjectPathsDict().set_app_path(Path(__file__).parents[2])
_MY_APP[ProjectPathsDict.DIST_PATH] = _MY_APP[ProjectPathsDict.APP_PATH] / 'dist'
_MY_APP[ProjectPathsDict.CONFIG_PATH] = _MY_APP[ProjectPathsDict.DIST_PATH] / 'config'
_MY_APP[ProjectPathsDict.CONFIG_FILE_PATH] = _MY_APP[ProjectPathsDict.CONFIG_PATH] / 'config.toml'
MY_CFG: ConfigFileManager = ConfigFileManager(_MY_APP[ProjectPathsDict.CONFIG_FILE_PATH])
load_dotenv(
    dotenv_path= _MY_APP[ProjectPathsDict.DIST_PATH] / '.env',
    override= False
)

# ENV VARS
CAMERA: int = int(getenv(EnvVars.CAMERA.value, 0))
GPIO_CHIP: Optional[str] = getenv(EnvVars.GPIO_CHIP.value, None)
_aux: Optional[str] = getenv(EnvVars.ACTUATOR_PIN.value, None)
ACTUATOR_PIN: Optional[int] = _aux if _aux is None else int(_aux)
_aux = getenv(EnvVars.CAMERA_SENSOR_PIN.value, None)
CAMERA_SENSOR_PIN: Optional[int] = _aux if _aux is None else int(_aux)
_aux = getenv(EnvVars.ACTUATOR_SENSOR_PIN.value, None)
ACTUATOR_SENSOR_PIN: Optional[int] = _aux if _aux is None else int(_aux)
SENSORS_INTERVAL: int = int(getenv(EnvVars.SENSORS_INTERVAL.value, 60000))

# LOGGING LEVELS
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env(EnvVars.LOGGING_LVL.value)
set_yolo_manager_logging_level(logging.WARNING)
set_yolo_manager_logs_path('cameraApp.log')
set_yolo_manager_logging_level(LOGGING_LVL)
save_yolo_manager_logs(True)

my_logger = MyLogger(
    logger_name= f'CameraApp',
    logging_level= LOGGING_LVL,
    file_path= 'cameraApp.log',
    save_logs= True
)
