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


import os
import shutil
import tempfile
from pathlib import Path

TEMP_DIR: Path = Path(tempfile.mkdtemp(prefix= 'pytest-parts-sorter-api'))

def pytest_configure() -> None:
    (TEMP_DIR / 'images' / 'production').mkdir(parents=True)
    (TEMP_DIR / 'models').mkdir(parents=True)
    os.environ['STATIC_PATH'] = str(TEMP_DIR)
    os.environ['DATABASE_URL'] = ''

def pytest_unconfigure() -> None:
    shutil.rmtree(TEMP_DIR)
    os.environ.pop('STATIC_PATH', None)
    os.environ.pop('DATABASE_URL', None)
