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


from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ModelMetadataDict(BaseModel):
    date: datetime
    camera_width: int
    camera_height: int
    brightness: float
    contrast: float
    saturation: float
    exposure: float
    wb: float
    dataset: str
    model_type: str
    filters: tuple[str]
    filters_attrs: dict[str, dict[str, Any]]
    task: str
    name: dict[int, str]


class NCNNMetadataDict(BaseModel):
    description: str
    author: str
    date: datetime
    version: str
    license: str
    docs: str
    stride: int
    task: str
    batch: int
    imgsz: tuple[int, int]
    names: dict[int, str]
    args: dict[str, Any]
    channels: int
