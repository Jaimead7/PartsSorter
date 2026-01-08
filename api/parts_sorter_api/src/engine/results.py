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


from typing import Optional, Protocol, Sequence

import numpy as np
from typing_extensions import TypedDict


class SpeedDict(TypedDict):
    preprocess: float
    inference: float
    postprocess: float


class BoxesType(Protocol):
    data: np.ndarray
    orig_shape: tuple[int, int]
    @property
    def xyxy(self) -> np.ndarray: ...
    @property
    def conf(self) -> np.ndarray: ...
    @property
    def cls(self) -> np.ndarray: ...
    @property
    def xywh(self) -> np.ndarray: ...
    @property
    def xyxyn(self) -> np.ndarray: ...
    @property
    def xywhn(self) -> np.ndarray: ...


class MyBoxes:
    def __init__(
        self,
        boxes: np.ndarray,  # [x0, y0, x1, y1, conf, id] x n
        orig_shape: tuple[int, int],
        names: dict[int, str]
    ) -> None:
        self.data: np.ndarray = boxes
        self.orig_shape: tuple[int, int] = orig_shape[:2]
        self.names: dict[int, str] = names

    def __repr__(self) -> str:
        result: str = 'MyBoxes object:\n'
        result += f'cls: {self.cls_names}\n'
        result += f'data: {self._parse_np_str(self.data)}\n'
        result += f'orig_shape: {self.orig_shape}\n'
        result += f'xywh: {self._parse_np_str(self.xywh)}\n'
        result += f'xywhn: {self._parse_np_str(self.xywhn)}\n'
        result += f'xyxy: {self._parse_np_str(self.xyxy)}\n'
        result += f'xyxyn: {self._parse_np_str(self.xyxyn)}'
        return result

    @staticmethod
    def _parse_np_str(array: np.ndarray) -> str:
        return np.array2string(
            array,
            separator=', ',
            precision=4,
            suppress_small=True
        )

    @property
    def xyxy(self) -> np.ndarray:
        return self.data[:, :4]

    @property
    def conf(self) -> np.ndarray:
        return self.data[:, -2]

    @property
    def cls(self) -> np.ndarray:
        return self.data[:, -1]

    @property
    def cls_names(self) -> Sequence[str]:
        return tuple(self.names[id] for id in self.cls)

    @property
    def xywh(self) -> np.ndarray:
        return self.xyxy2xywh(self.xyxy)

    @property
    def xyxyn(self) -> np.ndarray:
        return self.norm_coords(self.xyxy, self.orig_shape)

    @property
    def xywhn(self) -> np.ndarray:
        return self.norm_coords(self.xywh, self.orig_shape)

    @staticmethod
    def xyxy2xywh(xyxy: np.ndarray) -> np.ndarray:
        wh = xyxy[:, 2:] - xyxy[:, :2]
        xy = xyxy[:, :2] + wh / 2
        return np.concatenate((xy, wh), axis=1)

    @staticmethod
    def xywh2xyxy(xywh: np.ndarray) -> np.ndarray:
        x0y0 = xywh[:, :2] - xywh[:, 2:] / 2
        x1y1 = x0y0 + xywh[:, 2:]
        return np.concatenate((x0y0, x1y1), axis=1)

    @staticmethod
    def norm_coords(coords: np.ndarray, img_size: tuple[int, int]) -> np.ndarray:
        norm_array: np.ndarray = np.array(img_size + img_size)
        return coords / norm_array


class ResutlsType(Protocol):
    orig_img: np.ndarray
    orig_shape: tuple[int, int]
    names: dict[int, str]
    boxes: Optional[BoxesType]
    speed: SpeedDict


class MyResults:
    def __init__(
        self,
        orig_img: np.ndarray,
        names: dict[int, str],
        boxes: np.ndarray,  # [x1, y1, x2, y2, conf, id] x n
        speed: SpeedDict
    ) -> None:
        self.orig_img: np.ndarray = orig_img
        self.orig_shape: tuple[int, int] = orig_img.shape
        self.names: dict[int, str] = names
        self.speed: SpeedDict = speed
        self.boxes: Optional[BoxesType] = MyBoxes(
            boxes= boxes,
            orig_shape= self.orig_shape,
            names= self.names
        )


def extract_one_result(results: ResutlsType) -> tuple[Optional[int], Optional[float]]:
    if results.boxes is None:
        return (None, None)
    results_array: np.ndarray = results.boxes.data
    if len(results_array) == 0:
        return (None, None)
    # [x0, y0, x1, y1, conf, id] x n
    sort_array: np.ndarray = results_array[results_array[:, 4].argsort()[::-1]]
    best: np.ndarray = sort_array[0]
    #CHECK: check for all cases
    for result in sort_array:
        if result[0] < best[0]:
            best = result
    return (int(best[-1]), float(best[-2]))
