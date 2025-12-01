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


from typing import Any, Protocol

import cv2
import numpy as np


class ImageFilterFunction(Protocol):
    def __call__(self, img: np.ndarray, *args: Any, **kwargs: Any) -> np.ndarray:
        ...


def none_filter(
    img: np.ndarray
) -> np.ndarray:
    return img

def bgr2gray(
        img: np.ndarray
    ) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def gray2bgr(
        img: np.ndarray
    ) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

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

def cut(
        img: np.ndarray,
        width: int = 640,
        height: int = 640
    ) -> np.ndarray:
        ... #TODO: Do cut filter
        return img

def border(
        img: np.ndarray,
        width: int = 1,
        color: tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> np.ndarray:
        return cv2.copyMakeBorder(
            img,
            width,
            width,
            width,
            width,
            cv2.BORDER_CONSTANT,
            value= color
        )

def padding(
        img: np.ndarray,
        target_height: int,
        target_width: int,
        color: tuple[int, int, int, int] = (255, 255, 255, 255)
    ) -> np.ndarray:
        height: int
        width: int
        height, width = img.shape[:2]
        delta_h: int = target_height - height
        delta_h = delta_h if delta_h >= 0 else 0
        delta_w: int = target_width - width
        delta_w = delta_w if delta_w >= 0 else 0
        return cv2.copyMakeBorder(
            img,
            delta_h // 2,
            delta_h - (delta_h // 2),
            delta_w // 2,
            delta_w - (delta_w // 2),
            cv2.BORDER_CONSTANT,
            value= color
        )

IMAGE_FILTERS: dict[str, ImageFilterFunction] = {
    'NONE': none_filter,
    'GRAY': bgr2gray,
    'COLOR': gray2bgr,
    'RESIZE': resize,
    'CUT': cut,
    'BORDER': border,
    'PADDING': padding,
}

def image_filter_factory(name: str) -> ImageFilterFunction:
    try:
        return IMAGE_FILTERS[name.upper()]
    except KeyError:
        return IMAGE_FILTERS['NONE']
