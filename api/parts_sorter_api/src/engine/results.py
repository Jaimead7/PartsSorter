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


from typing import Any, Optional, Protocol, runtime_checkable

import numpy as np
from typing_extensions import TypedDict

from .plot import plot_label, plot_rect


class SpeedDict(TypedDict):
    preprocess: float
    inference: float
    postprocess: float


@runtime_checkable
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
        orig_shape: tuple[int, int]  # (h, w)
    ) -> None:
        self.data: np.ndarray = boxes
        self.orig_shape: tuple[int, int] = orig_shape[:2]

    def __repr__(self) -> str:
        result: str = 'MyBoxes object:\n'
        result += f'cls: {self.cls}\n'
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


@runtime_checkable
class ResutlsType(Protocol):
    orig_img: np.ndarray
    orig_shape: tuple[int, int]
    names: dict[int, str]
    boxes: Optional[BoxesType]
    speed: SpeedDict

    def plot(
        self,
        conf: bool = True,
        line_width: float | None = None,
        font_size: float | None = None,
        font: str = "Arial.ttf",
        pil: bool = False,
        img: np.ndarray | None = None,
        im_gpu: Any = None,
        kpt_radius: int = 5,
        kpt_line: bool = True,
        labels: bool = True,
        boxes: bool = True,
        masks: bool = True,
        probs: bool = True,
        show: bool = False,
        save: bool = False,
        filename: str | None = None,
        color_mode: str = "class",
        txt_color: tuple[int, int, int] = (255, 255, 255),
    ) -> np.ndarray:
        ...


class MyResults:
    def __init__(
        self,
        orig_img: np.ndarray,
        names: dict[int, str],
        boxes: Optional[np.ndarray],  # [x1, y1, x2, y2, conf, id] x n
        speed: SpeedDict
    ) -> None:
        self.orig_img: np.ndarray = orig_img
        self.orig_shape: tuple[int, int] = orig_img.shape  # (h, w)
        self.names: dict[int, str] = names
        self.speed: SpeedDict = speed
        if boxes is None:
            self.boxes: Optional[BoxesType]  = None
        else:
            self.boxes = MyBoxes(
                boxes= boxes,
                orig_shape= self.orig_shape,
            )

    def plot(
        self,
        conf: bool = True,
        line_width: float | None = None,
        font_size: float | None = None,
        font: str = "Arial.ttf",
        pil: bool = False,
        img: np.ndarray | None = None,
        im_gpu: Any = None,
        kpt_radius: int = 5,
        kpt_line: bool = True,
        labels: bool = True,
        boxes: bool = True,
        masks: bool = True,
        probs: bool = True,
        show: bool = False,
        save: bool = False,
        filename: str | None = None,
        color_mode: str = "class",
        txt_color: tuple[int, int, int] = (255, 255, 255),
    ) -> np.ndarray:
        if img is None:
            img = self.orig_img
        if self.boxes is None:
            return img
        for rect in self.boxes.data:
            if boxes:
                plot_rect(
                    img= img,
                    rect= rect,
                    line_width= line_width
                )
            if labels or conf:
                plot_label(
                    img= img,
                    rect= rect,
                    names= self.names,
                    conf= conf,
                    labels= labels,
                    font_size= font_size,
                    line_width= line_width
                )
        return img


def extract_first_result(results: ResutlsType) -> tuple[Optional[int], Optional[float]]:
    if results.boxes is None:
        return (None, None)
    results_array: np.ndarray = results.boxes.data
    if len(results_array) == 0:
        return (None, None)
    first: np.ndarray = results_array[0]
    # [x0, y0, x1, y1, conf, id] x n
    return (int(first[-1]), float(first[-2]))
