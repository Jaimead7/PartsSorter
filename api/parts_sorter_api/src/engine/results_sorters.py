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


from collections.abc import Callable, Generator, Sequence
from typing import Protocol, runtime_checkable

import numpy as np
from pyUtils import NoInstantiable

from ..dependencies.config import my_logger
from .results import BoxesType, ResutlsType


@runtime_checkable
class ResultsSorterFunction(Protocol):
    def __call__(self, results: ResutlsType) -> ResutlsType:
        ...


class ResultsSorterRegistry(NoInstantiable):
    _sorters: dict[str, ResultsSorterFunction] = {}

    @staticmethod
    def no_sort(results: ResutlsType) -> ResutlsType:
        return results

    @classmethod
    def register(cls, name: str) -> Callable[[ResultsSorterFunction], ResultsSorterFunction]:
        def decorator(func: ResultsSorterFunction) -> ResultsSorterFunction:
            if name.upper() in cls._sorters:
               my_logger.warning(f'ResultsSorter "{name.upper()}" is already registered. It will be overwritten.')
            cls._sorters[name.upper()] = func
            return func
        return decorator

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._sorters.pop(name.upper(), None)

    @classmethod
    def get(cls, name: str) -> ResultsSorterFunction:
        return cls._sorters.get(name.upper(), cls.no_sort)

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._sorters.keys())

    @classmethod
    def clear(cls) -> None:
        cls._sorters.clear()


def apply_results_sorters(
    results: ResutlsType,
    sorters: str | Sequence[str]
) -> ResutlsType:
    if isinstance(sorters, str):
        sorters = (sorters,)
    sorters_fnc: Generator[ResultsSorterFunction, None, None] = (
        ResultsSorterRegistry.get(name)
        for name in sorters
    )
    for fnc in sorters_fnc:
        results = fnc(results)
    return results

@ResultsSorterRegistry.register('CONF')
def by_conf(results: ResutlsType) -> ResutlsType:
    if results.boxes is None or len(results.boxes.data) == 0:
        return results
    boxes_data: np.ndarray = results.boxes.data
    sort_boxes: np.ndarray = boxes_data[boxes_data[:, 4].argsort()[::-1]]
    results.boxes.data = sort_boxes
    return results

@ResultsSorterRegistry.register('CENTER')
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
