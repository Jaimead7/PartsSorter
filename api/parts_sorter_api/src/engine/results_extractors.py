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
from enum import IntEnum, unique
from functools import cache
from typing import ClassVar, Optional, Protocol

import numpy as np
from pydantic import BaseModel, field_validator
from pyUtils import NoInstantiable

from ..dependencies.config import my_logger
from ..dependencies.func import to_title
from .results import ResultsType


@unique
class ExtractorsWarnings(IntEnum):
    OK = 0
    OVERLAP = -1
    CLOSE = -2

    @cache
    @classmethod
    def to_dict(cls) -> dict[str, int]:
        return {
            name: member.value
            for name, member in cls.__members__.items()
        }

    @cache
    @classmethod
    def get_all_names(cls) -> list[str]:
        return [
            to_title(name)
            for name in cls.to_dict().keys()
        ]

    @classmethod
    def validate_name(cls, name: str) -> Optional[str]:
        name = to_title(name)
        if name in cls.get_all_names():
            return name
        return None


class ExtractedResult(BaseModel):
    id: Optional[int] = None
    trust: Optional[float] = None
    warning: ExtractorsWarnings = ExtractorsWarnings.OK

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None or v >= 0:
            return v
        raise ValueError(f'{cls.__name__}.id must be Optional[int].')

    @field_validator('trust')
    @classmethod
    def validate_trust(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0. or v > 1.):
            raise ValueError(f'{cls.__name__}.trust must be [0, 1] or None.')
        return v

    def unpack(self) -> tuple[Optional[int], Optional[float], ExtractorsWarnings]:
        return (self.id, self.trust, self.warning)


class ResultsExtractorFunction(Protocol):
    def __call__(self, results: ResultsType) -> ExtractedResult: ...


class ResultsExtractorRegistry(NoInstantiable):
    _extractors: ClassVar[dict[str, ResultsExtractorFunction]] = {}

    @staticmethod
    def no_extract(results: ResultsType) -> ExtractedResult:
        return ExtractedResult()

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

    @classmethod
    def extract(cls, results: ResultsType, extractor: str) -> ExtractedResult:
        return cls.get(extractor)(results)


@ResultsExtractorRegistry.register('FIRST')
def extract_first_result(results: ResultsType) -> ExtractedResult:
    # [x0, y0, x1, y1, conf, id] x n
    if results.boxes is None:
        return ExtractedResult()
    results_array: np.ndarray = results.boxes.data
    if len(results_array) == 0:
        return ExtractedResult()
    first: np.ndarray = results_array[0]
    return ExtractedResult(
        id = first[-1],
        trust = first[-2],
        warning= ExtractorsWarnings.OK
    )

@ResultsExtractorRegistry.register('ALONE')
def extract_first_result_alone(results: ResultsType) -> ExtractedResult:
    # [x0, y0, x1, y1, conf, id] x n
    threshold: int = 10  #TODO: use as param
    if results.boxes is None:
        return ExtractedResult()
    boxes: np.ndarray = results.boxes.data
    if boxes.shape[0] == 1:
        return ExtractedResult(
            id= boxes[0,-1],
            trust= boxes[0,-2],
            warning= ExtractorsWarnings.OK
        )
    boxes_norm: np.ndarray = np.column_stack([
        np.minimum(boxes[:, 0], boxes[:, 2]),
        np.minimum(boxes[:, 1], boxes[:, 3]),
        np.maximum(boxes[:, 0], boxes[:, 2]),
        np.maximum(boxes[:, 1], boxes[:, 3])
    ])
    base: np.ndarray = boxes_norm[0]
    others: np.ndarray = boxes_norm[1:]
    warning: ExtractorsWarnings = ExtractorsWarnings.OK
    if squares_overlap(base, others):
        warning = ExtractorsWarnings.OVERLAP
    scale_array: np.ndarray = np.array([-threshold, -threshold, threshold, threshold])
    if squares_overlap(base + scale_array, others):
        warning = ExtractorsWarnings.CLOSE
    return ExtractedResult(
        id= boxes[0,-1],
        trust= boxes[0,-2],
        warning= warning
    )

def squares_overlap(base: np.ndarray, others: np.ndarray) -> bool:
    overlap_x: np.ndarray = np.maximum(base[0], others[:,0]) < np.minimum(base[2], others[:,2])
    overlap_y: np.ndarray = np.maximum(base[1], others[:,1]) < np.minimum(base[3], others[:,3])
    overlap: np.ndarray = overlap_x & overlap_y
    return bool(np.any(overlap))
