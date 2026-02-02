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
from typing import Any, ClassVar, Protocol

import cv2
import numpy as np
from pyUtils import NoInstantiable, my_logger


class ImageFilterFunction(Protocol):
    def __call__(self, img: np.ndarray, *args: Any, **kwargs: Any) -> np.ndarray:
        ...


class ImageFilterRegistry(NoInstantiable):
    _filters: ClassVar[dict[str, ImageFilterFunction]] = {}

    @staticmethod
    def no_filter(img: np.ndarray) -> np.ndarray:
        return img

    @classmethod
    def register(cls, name: str) -> Callable[[ImageFilterFunction], ImageFilterFunction]:
        def decorator(func: ImageFilterFunction) -> ImageFilterFunction:
            if name.upper() in cls._filters:
                my_logger.warning(f'ImageFilter "{name.upper()}" is already registered. It will be overwritten.')
            cls._filters[name.upper()] = func
            return func
        return decorator

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._filters.pop(name.upper(), None)

    @classmethod
    def get(cls, name: str) -> ImageFilterFunction:
        return cls._filters.get(name.upper(), cls.no_filter)

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._filters.keys())

    @classmethod
    def clear(cls) -> None:
        cls._filters.clear()


@ImageFilterRegistry.register('RESIZE')
def resize(
    img: np.ndarray,
    width: int = 640,
    height: int = 640
) -> np.ndarray:
    return cv2.resize(
        img,
        (width, height),
        interpolation= cv2.INTER_LINEAR
    )

@ImageFilterRegistry.register('REDIM')
def redim(
    img: np.ndarray,
    height: int = 640,
    width: int = 640,
    gray: int = 114
) -> np.ndarray:
    org_h: int
    org_w: int
    org_h, org_w = img.shape[:2]
    scale: float = min(width/org_w, height/org_h)
    new_w = int(org_w * scale)
    new_h = int(org_h * scale)
    img_resized: np.ndarray = resize(img= img, width= new_w, height= new_h)
    result: np.ndarray = np.ones((height, width, 3), dtype= np.uint8) * gray
    result[:new_h, :new_w] = img_resized
    return result

@ImageFilterRegistry.register('GRAY')
def bgr2gray(
    img: np.ndarray
) -> np.ndarray:
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

@ImageFilterRegistry.register('COLOR')
def gray2bgr(
    img: np.ndarray
) -> np.ndarray:
    if len(img.shape) == 3:
        return img
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

@ImageFilterRegistry.register('RGB')
def bgr2rgb(
    img: np.ndarray
) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

@ImageFilterRegistry.register('BGR')
def rgb2bgr(
    img: np.ndarray
) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

@ImageFilterRegistry.register('CUT')
def cut(
    img: np.ndarray,
    width: int = 640,
    height: int = 640
) -> np.ndarray:
    ... #TODO: Do cut filter
    return img
