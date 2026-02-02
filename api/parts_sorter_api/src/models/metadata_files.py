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
