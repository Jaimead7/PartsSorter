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


from collections.abc import Callable
from typing import ClassVar, Optional, Protocol

import numpy as np
from pydantic import BaseModel, field_validator
from pyUtils import NoInstantiable

from ..dependencies.config import my_logger
from .results import ResultsType


class ClassResult(BaseModel):
    id: Optional[int] = None
    trust: Optional[float] = None

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < -1:
            raise ValueError(f'{cls.__name__}.id must be Optional[int].')
        return v

    @field_validator('trust')
    @classmethod
    def validate_trust(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0. or v > 1.):
            raise ValueError(f'{cls.__name__}.trust must be [0, 1] or None.')
        return v

    def unpack(self) -> tuple[Optional[int], Optional[float]]:
        return (self.id, self.trust)


class ResultsExtractorFunction(Protocol):
    def __call__(self, results: ResultsType) -> ClassResult:
        ...


class ResultsExtractorRegistry(NoInstantiable):
    _extractors: ClassVar[dict[str, ResultsExtractorFunction]] = {}

    @staticmethod
    def no_extract(results: ResultsType) -> ClassResult:
        return ClassResult()

    @classmethod
    def register(cls, name: str) -> Callable[[ResultsExtractorFunction], ResultsExtractorFunction]:
        def decorator(func: ResultsExtractorFunction) -> ResultsExtractorFunction:
            if name.upper() in cls._extractors:
               my_logger.warning(f'ResultsExtractor "{name.upper()}" is already registered. It will be overwritten.')
            cls._extractors[name.upper()] = func
            return func
        return decorator

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._extractors.pop(name.upper(), None)

    @classmethod
    def get(cls, name: str) -> ResultsExtractorFunction:
        return cls._extractors.get(name.upper(), cls.no_extract)

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._extractors.keys())

    @classmethod
    def clear(cls) -> None:
        cls._extractors.clear()


@ResultsExtractorRegistry.register('FIRST')
def extract_first_result(results: ResultsType) -> ClassResult:
    # [x0, y0, x1, y1, conf, id] x n
    if results.boxes is None:
        return ClassResult()
    results_array: np.ndarray = results.boxes.data
    if len(results_array) == 0:
        return ClassResult()
    first: np.ndarray = results_array[0]
    return ClassResult(id = first[-1], trust = first[-2])

@ResultsExtractorRegistry.register('ALONE')
def extract_first_result_alone(results: ResultsType) -> ClassResult:
    # [x0, y0, x1, y1, conf, id] x n
    threshold: int = 10
    if results.boxes is None:
        return ClassResult()
    boxes: np.ndarray = results.boxes.data
    if boxes.shape[0] == 1:
        return ClassResult(id= boxes[0,-1], trust= boxes[0,-2])
    x0: np.ndarray = boxes[:, 0]
    y0: np.ndarray = boxes[:, 1]
    x1: np.ndarray = boxes[:, 2]
    y1: np.ndarray = boxes[:, 3]
    xmin: np.ndarray = np.minimum(x0, x1)
    ymin: np.ndarray = np.minimum(y0, y1)
    xmax: np.ndarray = np.maximum(x0, x1)
    ymax: np.ndarray = np.maximum(y0, y1)
    base_xmin: int = xmin[0] - threshold
    base_ymin: int = ymin[0] - threshold
    base_xmax: int = xmax[0] + threshold
    base_ymax: int = ymax[0] + threshold
    other_xmin: np.ndarray = xmin[1:]
    other_ymin: np.ndarray = ymin[1:]
    other_xmax: np.ndarray = xmax[1:]
    other_ymax: np.ndarray = ymax[1:]
    overlap_x = np.maximum(base_xmin, other_xmin) < np.minimum(base_xmax, other_xmax)
    overlap_y = np.maximum(base_ymin, other_ymin) < np.minimum(base_ymax, other_ymax)
    overlap = overlap_x & overlap_y
    if np.any(overlap):
        return ClassResult(id= -1, trust= None)
    return ClassResult(id= boxes[0,-1], trust= boxes[0,-2])
