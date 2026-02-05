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


from collections.abc import Callable, Generator, Sequence
from typing import ClassVar, Protocol

import numpy as np
from pyUtils import NoInstantiable

from ..dependencies.config import my_logger
from .results import BoxesType, ResultsType


class ResultsSorterFunction(Protocol):
    def __call__(self, results: ResultsType) -> ResultsType:
        ...


class ResultsSorterRegistry(NoInstantiable):
    _sorters: ClassVar[dict[str, ResultsSorterFunction]] = {}

    @staticmethod
    def no_sort(results: ResultsType) -> ResultsType:
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
    results: ResultsType,
    sorters: str | Sequence[str]
) -> ResultsType:
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
def by_conf(results: ResultsType) -> ResultsType:
    if results.boxes is None or len(results.boxes.data) == 0:
        return results
    boxes_data: np.ndarray = results.boxes.data
    sort_boxes: np.ndarray = boxes_data[boxes_data[:, 4].argsort()[::-1]]
    results.boxes.data = sort_boxes
    return results

@ResultsSorterRegistry.register('CENTER')
def dis_center(results: ResultsType) -> ResultsType:
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
