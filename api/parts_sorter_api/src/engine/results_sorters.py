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


from typing import Protocol

import numpy as np

from .results import BoxesType, ResutlsType


class ResultsSorterFunction(Protocol):
    def __call__(self, results: ResutlsType) -> ResutlsType:
        ...


def no_sort(results: ResutlsType) -> ResutlsType:
    return results

def by_conf(results: ResutlsType) -> ResutlsType:
    if results.boxes is None or len(results.boxes.data) == 0:
        return results
    boxes_data: np.ndarray = results.boxes.data
    sort_boxes: np.ndarray = boxes_data[boxes_data[:, 4].argsort()[::-1]]
    results.boxes.data = sort_boxes
    return results

def dis_center(results: ResutlsType) -> ResutlsType:
    def get_center_distances(boxes: BoxesType) -> np.ndarray:
        x_centers: np.ndarray = (boxes.data[:, 0] + boxes.data[:, 2]) / 2
        y_centers: np.ndarray = (boxes.data[:, 1] + boxes.data[:, 3]) / 2
        centers: np.ndarray = np.column_stack((x_centers, y_centers))
        img_center: np.ndarray = np.array(
            [boxes.orig_shape[1] / 2,
             boxes.orig_shape[0] / 2]
        )
        return np.linalg.norm(centers - img_center, axis= 1)
    if results.boxes is None or len(results.boxes.data) == 0:
        return results
    distances: np.ndarray = get_center_distances(boxes= results.boxes)
    boxes_data: np.ndarray = results.boxes.data
    sort_boxes: np.ndarray = boxes_data[distances.argsort()]
    results.boxes.data = sort_boxes
    return results


RESULTS_SORTERS: dict[str, ResultsSorterFunction] = {
    'NONE': no_sort,
    'CONF': by_conf,
    'CENTER': dis_center
}

def results_sorter_factory(name: str) -> ResultsSorterFunction:
    try:
        return RESULTS_SORTERS[name.upper()]
    except KeyError:
        return no_sort
