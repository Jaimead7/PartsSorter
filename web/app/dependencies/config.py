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

from pyUtils import (MyLogger, save_pyutils_logs, set_pyutils_logging_level,
                     set_pyutils_logs_path)


class EnvVars(Enum):
    LOGGING_LVL = 'LOGGING_LVL'
    SERVER_IP = 'SERVER_IP'
    SERVER_PORT = 'SERVER_PORT'
    API_URL = 'API_URL'


# LOGGING
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env(EnvVars.LOGGING_LVL.value)

my_logger: MyLogger = MyLogger(
    logger_name= 'web',
    logging_level= LOGGING_LVL
)

def set_web_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_pyutils_logs_path(new_path)

def save_web_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_pyutils_logs(value)

def set_web_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_pyutils_logging_level(lvl)

set_web_logging_level(logging.WARNING)
set_web_logs_path('web.log')
set_web_logging_level(LOGGING_LVL)
save_web_logs(True)

# ENV VARS
SERVER_IP: str = getenv(EnvVars.SERVER_IP.value, 'localhost')
SERVER_PORT: int = int(getenv(EnvVars.SERVER_PORT.value, 5000))
API_URL: str = getenv(EnvVars.API_URL.value, 'localhost:8000')
