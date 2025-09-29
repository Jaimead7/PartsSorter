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


from typing import Optional

import numpy as np
from torch import Tensor
from ultralytics import YOLO
from ultralytics.engine.results import Results

from ..models.database import Image, Model


#TODO: Abstract
async def inspect(
    db_img: Image,
    db_model: Model,
) -> Optional[int]:
    model = YOLO(
        db_model.internal_absolute_ncnn_path,
        task= 'detect'
    )
    return await get_best_result_class_n(model(db_img.internal_absolute_path)[0])

async def get_best_result_class_n(
    results: Results
) -> Optional[int]:
    if results.boxes is None:
        return None
    if isinstance(results.boxes.data, Tensor):
        results_array: np.ndarray = results.boxes.data.numpy()
    else:
        results_array = results.boxes.data
    best: np.ndarray = results_array[0]
    #result = np.ndarray(x0, y0, x1, y1, conf, obj_n)
    for result in results_array:
        if result[-2] > best[-2]:
            best = result
    return int(best[-1])
