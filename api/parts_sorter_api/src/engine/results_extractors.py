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


from collections.abc import Callable, Generator
from typing import Any, ClassVar, Optional, Protocol

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
        if v is not None and v < 0:
            raise ValueError(f'{cls.__name__}.id must be positive.')
        return v

    @field_validator('trust')
    @classmethod
    def validate_trust(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0. or v > 1.):
            raise ValueError(f'{cls.__name__}.trust must be [0, 1].')
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
    if results.boxes is None:
        return ClassResult()
    results_array: np.ndarray = results.boxes.data
    if len(results_array) == 0:
        return ClassResult()
    first: np.ndarray = results_array[0]
    # [x0, y0, x1, y1, conf, id] x n
    return ClassResult(id = first[-1], trust = first[-2])
