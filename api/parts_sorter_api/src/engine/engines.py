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


from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import Any, Generator, Iterable, Optional, Protocol

import cv2
import ncnn
import numpy as np
import yaml

from ..dependencies.config import my_logger
from ..models.metadata_files import NCNNMetadataDict
from .filters import bgr2rgb, gray2bgr, redim
from .results import MyBoxes, MyResults, ResutlsType, SpeedDict


class ModelEngine(Protocol):
    def __init__(
        self,
        model: str | Path,
        *args: Any,
        **kwargs: Any
    ) -> None: ...

    def __call__(
        self,
        source: np.ndarray | str | Path | list | tuple,
        *args: Any,
        **kwargs: Any
    ) -> list[ResutlsType]: ...


class NCCEngine:
    GLOBAL_CONF_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.75

    def __init__(
        self,
        model: str | Path
    ) -> None:
        self.path: Path = Path(model)
        self._load()

    def __call__(
        self,
        source: np.ndarray | str | Path | list | tuple
    ) -> list[ResutlsType]:
        sources: Iterable[np.ndarray | str | Path]
        if not isinstance(source, tuple | list):
            sources = [source]
        else:
            sources = source
        sources_arrays: Generator[np.ndarray, None, None] = self.get_sources_arrays(sources)
        results: list[ResutlsType] = []
        for raw_img in sources_arrays:
            speed: SpeedDict = SpeedDict(
                preprocess= 0,
                inference= 0,
                postprocess= 0
            )
            start_time: datetime = datetime.now(timezone.utc)
            in_img: ncnn.Mat = self.preprocess(raw_img)
            speed['preprocess'] = (datetime.now(timezone.utc) - start_time).microseconds / 1000.
            start_time = datetime.now(timezone.utc)
            with self._net.create_extractor() as ex:
                ex.input('in0', in_img)
                out0: ncnn.Mat
                ret: int
                ret, out0 = ex.extract('out0')
            speed['inference'] = (datetime.now(timezone.utc) - start_time).microseconds / 1000.
            start_time = datetime.now(timezone.utc)
            out_array: np.ndarray = self.parse_ncnn_out(out0)
            boxes: np.ndarray = self.filter_boxes(out_array)
            speed['postprocess'] = (datetime.now(timezone.utc) - start_time).microseconds / 1000.
            result: ResutlsType = MyResults(
                orig_img= raw_img,
                names= self.metadata.names,
                boxes= boxes,
                speed= speed
            )
            results.append(result)
        return results

    @cached_property
    def metadata_path(self) -> Path:
        return self.path / 'metadata.yaml'

    @cached_property
    def bin_path(self) -> Path:
        return self.path / 'model.ncnn.bin'

    @cached_property
    def param_path(self) -> Path:
        return self.path / 'model.ncnn.param'

    @cached_property
    def metadata(self) -> NCNNMetadataDict:
        return self.get_ncnn_metadata(self.path)

    @staticmethod
    def get_ncnn_metadata(ncnn_model_path: Path) -> NCNNMetadataDict:
        ncnn_metadata_path: Path = ncnn_model_path / 'metadata.yaml'
        if not ncnn_metadata_path.is_file():
            msg: str = f'"{ncnn_metadata_path}" does\'t exists.'
            my_logger.error(msg)
            raise FileNotFoundError(msg)
        try:
            with open(ncnn_model_path / 'metadata.yaml', 'r') as f:
                return NCNNMetadataDict(**yaml.safe_load(f))
        except Exception as e:
            msg: str = f'"{ncnn_metadata_path}" is not a valid ncnn metadata file.'
            my_logger.error(msg)
            raise ImportError(msg)

    def _load(self) -> None:
        self._net: ncnn.Net = ncnn.Net()
        self._net.load_param(str(self.param_path))
        self._net.load_model(str(self.bin_path))

    def get_sources_arrays(
        self,
        sources: Iterable[np.ndarray | str | Path]
    ) -> Generator[np.ndarray, None, None]:
        for source in sources:
            if isinstance(source, np.ndarray):
                yield source
                continue
            try:
                img: Optional[np.ndarray] = cv2.imread(str(source))
                if img is None:
                    raise ValueError(f'Could not read image from "{str(source)}".')
                yield img
            except Exception as e:
                msg: str = f'Error reading image "{source}": {str(e)}'
                my_logger.error(msg)

    def check_in_shape(self, img: np.ndarray) -> np.ndarray:
        exp_shape: tuple[int, int, int] = (*self.metadata.imgsz, self.metadata.channels)
        shape: tuple[int, ...] = img.shape
        if exp_shape == img.shape:
            return img
        if len(shape) == 2:
            img = gray2bgr(img)
        if len(shape) != 3:
            msg: str = f'Input img should be (h, w, 3) not {shape}.'
            my_logger.error(msg)
            raise AttributeError(msg)
        img = redim(
            img= img,
            height= exp_shape[0],
            width= exp_shape[1]
        )
        return img

    def preprocess(
        self,
        source: np.ndarray
    ) -> ncnn.Mat:
        img_proc: np.ndarray = source
        img_proc = self.check_in_shape(img_proc)
        img_proc = bgr2rgb(img_proc)
        img_proc = img_proc.transpose(2, 0, 1)
        img_proc = np.ascontiguousarray(img_proc)
        img_proc = img_proc.astype(np.float32) / 255.0
        return ncnn.Mat(img_proc).clone()

    def parse_ncnn_out(
        self,
        model_out
    ) -> np.ndarray:
        model_out_array: np.ndarray = np.array(model_out).T
        xywh: np.ndarray = model_out_array[:, :4]
        xyxy: np.ndarray = MyBoxes.xywh2xyxy(xywh)
        all_conf: np.ndarray = model_out_array[:, 4:]
        max_conf: np.ndarray = np.max(all_conf, axis= 1, keepdims= True)
        max_index: np.ndarray = np.argmax(all_conf, axis= 1, keepdims= True)
        return np.hstack((xyxy, max_conf, max_index))

    def filter_boxes(
        self,
        boxes: np.ndarray
    ) -> np.ndarray:
        mask = boxes[:, 4] > self.GLOBAL_CONF_THRESHOLD
        pot_boxes: np.ndarray = boxes[mask]
        filter_boxes: np.ndarray = self.nms(pot_boxes)
        return filter_boxes

    def nms(
        self,
        boxes: np.ndarray
    ) -> np.ndarray:
        x0: np.ndarray = boxes[:, 0]
        y0: np.ndarray = boxes[:, 1]
        x1: np.ndarray = boxes[:, 2]
        y1: np.ndarray = boxes[:, 3]
        scores: np.ndarray = boxes[:, 4]
        areas: np.ndarray = (x1 - x0) * (y1 - y0)
        order: np.ndarray = scores.argsort()[::-1]
        keep: list[int] = []
        while order.size > 0:
            i: int = order[0]
            keep.append(i)
            xx0: np.ndarray = np.maximum(x0[i], x0[order[1:]])
            yy0: np.ndarray = np.maximum(y0[i], y0[order[1:]])
            xx1: np.ndarray = np.minimum(x1[i], x1[order[1:]])
            yy1: np.ndarray = np.minimum(y1[i], y1[order[1:]])
            w: np.ndarray = np.maximum(0.0, xx1 - xx0)
            h: np.ndarray = np.maximum(0.0, yy1 - yy0)
            intersection: np.ndarray = w * h
            union: np.ndarray = areas[i] + areas[order[1:]] - intersection
            iou: np.ndarray = intersection / union
            inds = np.where(iou <= self.IOU_THRESHOLD)[0]
            order = order[inds + 1]
        return boxes[keep]
