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


from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, Optional, Self, cast

import cv2
import numpy as np
import yaml
from pyUtils import NoInstantiable

from ..dependencies.config import my_logger
from ..models.metadata_files import ModelMetadataDict
from .engines import ModelEngine, NCCEngine
from .filters import ImageFilterFunction, ImageFilterRegistry
from .results import ResultsType


class ModelManager(ABC):
    def __init__(self) -> None:
        self._path: Optional[Path] = None
        self._model_engine: Optional[ModelEngine] = None
        self.last_use: datetime = datetime.now(timezone.utc)

    @cached_property
    def path(self) -> Path:
        if self._path is None:
            msg: str = f'Path is not loaded. Try {self.__class__.__name__}.load(path).'
            my_logger.error(msg)
            raise AttributeError(msg)
        return self._path

    @property
    def model_engine(self) -> ModelEngine:
        if self._model_engine is None:
            msg: str = f'Model engine is not loaded. Try {self.__class__.__name__}.load(path).'
            my_logger.error(msg)
            raise AttributeError(msg)
        return self._model_engine

    @cached_property
    def name(self) -> str:
        return self.path.name

    @cached_property
    def metadata_path(self) -> Path:
        return self.path / 'metadata.yaml'

    @cached_property
    def metadata(self) -> ModelMetadataDict:
        return self.get_metadata(self.path)

    @cached_property
    def files(self) -> Iterable[Path]:
        return ()

    @cached_property
    def folders(self) -> Iterable[Path]:
        return ()

    @cached_property
    def filters(self) -> Sequence[tuple[ImageFilterFunction, dict[str, Any]]]:
        filters_names: tuple[str] = self.metadata.filters
        filters_attrs: dict[str, dict[str, Any]] = self.metadata.filters_attrs
        return tuple(
            (
                ImageFilterRegistry.get(filter_name),
                filters_attrs[filter_name]
            )
            for filter_name in filters_names
        )

    @staticmethod
    def get_metadata(model_path: Path) -> ModelMetadataDict:
        metadata_path: Path = model_path / 'metadata.yaml'
        if not metadata_path.is_file():
            msg: str = f'"{metadata_path}" does\'t exists.'
            my_logger.error(msg)
            raise FileNotFoundError(msg)
        try:
            with open(model_path / 'metadata.yaml', 'r') as f:
                return ModelMetadataDict(**yaml.safe_load(f))
        except Exception as e:
            msg: str = f'"{metadata_path}" is not a valid model metadata file.'
            my_logger.error(msg)
            raise ImportError(msg)

    @staticmethod
    def get_sources_arrays(
        sources: Sequence[np.ndarray | str | Path]
    ) -> Sequence[np.ndarray]:
        sources_arrays: list[np.ndarray] = []
        for source in sources:
            if isinstance(source, np.ndarray):
                sources_arrays.append(source)
                continue
            try:
                array: Optional[np.ndarray] = cv2.imread(str(source))
                if array is None:
                    raise ValueError(f'Could not read image from "{str(source)}".')
                sources_arrays.append(array)
            except Exception as e:
                msg: str = f'Error reading image "{source}": {str(e)}'
                my_logger.error(msg)
        return sources_arrays

    def validate(self) -> bool:
        if not self.path.is_dir():
            msg: str = f'Model folder "{self.path}" doesn\'t exist.'
            my_logger.error(msg)
            return False
        files_ok: bool = all(file.is_file() for file in self.files)
        folders_ok: bool = all(folder.is_dir() for folder in self.folders)
        if not files_ok or not folders_ok:
            msg: str = f'Model folder "{self.path}" doesn\'t have a valid structure.'
            my_logger.error(msg)
            return False
        return True

    def inspect(
        self,
        source: np.ndarray | str | Path | list | tuple
    ) -> list[ResultsType]:
        source_iter: Iterable[np.ndarray | str | Path]
        if isinstance(source, tuple | list):
            source_iter = source
        else:
            source_iter = [source]
        sources_arrays: Sequence[np.ndarray] = self.get_sources_arrays(source_iter)
        in_imgs: Sequence[np.ndarray] = self.apply_img_filters(sources_arrays)
        results: list[ResultsType] = self.model_engine(tuple(in_imgs))
        return results

    def apply_img_filters(
        self,
        sources_arrays: Sequence[np.ndarray]
    ) -> Sequence[np.ndarray]:
        def apply_filters(
            source_array: np.ndarray
        ) -> np.ndarray:
            result_array: np.ndarray = source_array
            for filter_fn, filter_attrs in self.filters:
                result_array = filter_fn(result_array, **filter_attrs)
            return result_array
        return tuple(apply_filters(source_array) for source_array in sources_arrays)

    @abstractmethod
    def load(self, path: Path) -> Self: ...


class ModelManagerRegistry(NoInstantiable):
    _managers: ClassVar[dict[str, type[ModelManager]]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[type[ModelManager]], type[ModelManager]]:
        def decorator(manager_cls: type[ModelManager]) -> type[ModelManager]:
            if name.upper() in cls._managers:
                my_logger.warning(f'ModelManager "{name.upper()}" is already registered. It will be overwritten.')
            cls._managers[name.upper()] = manager_cls
            return manager_cls
        return decorator

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._managers.pop(name.upper(), None)

    @classmethod
    def get(cls, name: str) -> Optional[type[ModelManager]]:
        return cls._managers.get(name.upper(), None)

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._managers.keys())

    @classmethod
    def clear(cls) -> None:
        cls._managers.clear()


class ModelsContainer(NoInstantiable):
    models: dict[str, ModelManager] = {}
    MAX_MODELS: int = 5

    @classmethod
    def get_model(
        cls,
        model_path: Path
    ) -> ModelManager:
        model_name: str = model_path.name
        try:
            return cls.models[model_name]
        except KeyError:
            pass
        model_type_name: str = ModelManager.get_metadata(model_path).model_type
        model_type: Optional[type[ModelManager]] = ModelManagerRegistry.get(model_type_name)
        if model_type is None:
            msg: str = f'No ModelManager for "{model_type_name}" is available.'
            my_logger.error(msg)
            raise KeyError(msg)
        model: ModelManager = model_type().load(model_path)
        cls.models[model_name] = model
        my_logger.info(f'"{model_name}" added to loaded models.')
        cls.clear_models()
        return cls.models[model_name]

    @classmethod
    def clear_models(cls) -> None:
        if len(cls.models) == 0:
            return
        if len(cls.models) <= cls.MAX_MODELS:
            return
        model_to_delete: str = list(cls.models.keys())[0]
        for name, model in cls.models.items():
            if model.last_use < cls.models[model_to_delete].last_use:
                model_to_delete = name
        cls.models.pop(model_to_delete)
        my_logger.info(f'"{model_to_delete}" deleted from loaded models.')


@ModelManagerRegistry.register('NCNN')
class NCNNModelManager(ModelManager):
    def __init__(self) -> None:
        super().__init__()
    
    @property
    def model_engine(self) -> NCCEngine:
        return cast(NCCEngine, super().model_engine)

    @cached_property
    def ncnn_folder_path(self) -> Path:
        return self.path / (self.name + '_ncnn_model')

    @cached_property
    def ncnn_metadata_path(self) -> Path:
        return self.ncnn_folder_path / 'metadata.yaml'

    @cached_property
    def ncnn_bin_path(self) -> Path:
        return self.ncnn_folder_path / 'model.ncnn.bin'

    @cached_property
    def ncnn_param_path(self) -> Path:
        return self.ncnn_folder_path / 'model.ncnn.param'

    @cached_property
    def files(self) -> Iterable[Path]:
        return (
            self.metadata_path,
            self.ncnn_metadata_path,
            self.ncnn_bin_path,
            self.ncnn_param_path
        )

    @cached_property
    def folders(self) -> Iterable[Path]:
        return (
            self.ncnn_folder_path,
        )

    def load(self, path: Path) -> Self:
        self._path = path
        if not self.validate():
            msg: str = 'Can\'t load a model. Folder not valid.'
            my_logger.error(msg)
            raise NotADirectoryError(msg)
        self._model_engine = NCCEngine(self.ncnn_folder_path)
        self.last_use = datetime.now(timezone.utc)
        return self
