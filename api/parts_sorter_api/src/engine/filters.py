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


from collections.abc import Callable
from typing import Any, Protocol

import cv2
import numpy as np
from pyUtils import NoInstantiable, my_logger


class ImageFilterFunction(Protocol):
    def __call__(self, img: np.ndarray, *args: Any, **kwargs: Any) -> np.ndarray:
        ...


class ImageFilterRegistry(NoInstantiable):
    _filters: dict[str, ImageFilterFunction] = {}

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
    def get_filter(cls, name: str) -> ImageFilterFunction:
        return cls._filters.get(name.upper(), cls.no_filter)

    @classmethod
    def list_filters(cls) -> list[str]:
        return sorted(cls._filters.keys())

    @classmethod
    def clear_registry(cls) -> None:
        cls._filters.clear()


def no_filter(
    img: np.ndarray
) -> np.ndarray:
    return img

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

def bgr2gray(
    img: np.ndarray
) -> np.ndarray:
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def gray2bgr(
    img: np.ndarray
) -> np.ndarray:
    if len(img.shape) == 3:
        return img
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def bgr2rgb(
    img: np.ndarray
) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def rgb2bgr(
    img: np.ndarray
) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

def cut(
    img: np.ndarray,
    width: int = 640,
    height: int = 640
) -> np.ndarray:
    ... #TODO: Do cut filter
    return img


IMAGE_FILTERS: dict[str, ImageFilterFunction] = {
    'NONE': no_filter,
    'RESIZE': resize,
    'REDIM': redim,
    'COLOR': gray2bgr,
    'GRAY': bgr2gray,
    'RGB': bgr2rgb,
    'BGR': rgb2bgr,
    'CUT': cut
}

def image_filter_factory(name: str) -> ImageFilterFunction:
    try:
        return IMAGE_FILTERS[name.upper()]
    except KeyError:
        return no_filter
