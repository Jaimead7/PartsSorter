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


from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

import yaml
from pyUtils import NoInstantiable
from sqlalchemy import JSON, Column
from sqlalchemy.sql import func
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from ..dependencies.config import (INTERNAL_IMAGES_FOLDER,
                                   INTERNAL_MODELS_FOLDER,
                                   STATIC_IMAGES_FOLDER, my_logger)
from ..dependencies.func import to_snakecase, to_title
from ..engine.results_extractors import ExtractorsWarnings
from .metadata_files import ModelMetadataDict


#TODO: Create response classes
#********** INSPECTION RESULTS **********
class InspectionResult(SQLModel, table= True):
    __tablename__: str = 'inspection_results' # type: ignore

    name: str = Field(
        primary_key= True,
        index= True,
    )

    images_of_result: Optional[list["Image"]] = Relationship(
        back_populates= 'result_of_image',
        sa_relationship_kwargs=dict(foreign_keys="[Image.inspection_result]")
    )
    images_of_true_result: Optional[list["Image"]] = Relationship(
        back_populates= 'true_result_of_image',
        sa_relationship_kwargs=dict(foreign_keys="[Image.true_result]")
    )
    model_classes_of_result: Optional[list['ModelClass']] = Relationship(
        back_populates= 'result_of_model_class'
    )
    origin_results_of_result: Optional[list['OriginResult']] = Relationship(
        back_populates= 'result_of_origin_result',
        sa_relationship_kwargs= {
            "cascade": "all, delete",
        }
    )


#********** ORIGINS **********
class Origin(SQLModel, table= True):
    __tablename__: str = 'origins' # type: ignore

    name: str = Field(
        primary_key= True,
        index= True,
    )
    model: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'models.name',
        ondelete= 'SET NULL'
    )
    params: Optional[dict[str, Any]] = Field(
        default= None,
        sa_type= JSON
    )

    images_of_origin: Optional[list['Image']] = Relationship(
        back_populates= 'origin_of_image'
    )
    alarms_of_origin: Optional[list['Alarm']] = Relationship(
        back_populates= 'origin_of_alarm'
    )
    origin_results_of_origin: Optional[list['OriginResult']] = Relationship(
        back_populates= 'origin_of_origin_result',
        sa_relationship_kwargs= {
            "cascade": "all, delete",
        }
    )
    model_of_origin: Optional['Model'] = Relationship(
        back_populates= 'origins_of_model',
    )


#********** MODEL **********
class Model(SQLModel, table= True):
    __tablename__: str = 'models' # type: ignore

    name: str = Field(
        primary_key= True
    )
    description: Optional[str] = Field(
        default= '',
        nullable= True
    )

    model_classes_of_model: Optional[list['ModelClass']] = Relationship(
        back_populates= 'model_of_model_class',
        sa_relationship_kwargs= {
            "cascade": "all, delete",
        }
    )
    origins_of_model: Optional[list['Origin']] = Relationship(
        back_populates= 'model_of_origin',
    )
    images_of_model: Optional[list['Image']] = Relationship(
        back_populates= 'model_of_image',
    )

    @property
    def internal_absolute_path(self) -> Path:
        """Get the complete path of the model directory inside the server.
        Returns:
            Path: Path of the model file.
        """
        return INTERNAL_MODELS_FOLDER / self.name

    @property
    def internal_absolute_ncnn_path(self) -> Path:
        """Get the complete path of the ncnn model directory inside the server.
        Returns:
            Path: Path of the model file.
        """
        return INTERNAL_MODELS_FOLDER / self.name / f'{self.name}_ncnn_model'

    @property
    def model_metadata(self) -> ModelMetadataDict:
        metadata_path: Path = self.internal_absolute_path / 'metadata.yaml'
        with open(metadata_path, 'r') as f:
            data: ModelMetadataDict = ModelMetadataDict(**yaml.safe_load(f))
        return data


#********** IMAGES **********
class ImageStatus(NoInstantiable):
    _status: dict[str, int] = {
        'captured': 0,
        'transition_push': 1,
        'transition_pass': 2,
        'actuator_push': 3,
        'actuator_pass': 4,
        'pushed': 5,
        'passed': 6,
        'error_overwrite': -1,
        'error_lost': -2,
        'error_skipped': -3,
    }

    captured: int = _status['captured']
    transition_push: int = _status['transition_push']
    transition_pass: int = _status['transition_pass']
    actuator_push: int = _status['actuator_push']
    actuator_pass: int = _status['actuator_pass']
    pushed: int = _status['pushed']
    passed: int = _status['passed']
    error_overwrite: int = _status['error_overwrite']
    error_lost: int = _status['error_lost']
    error_skipped: int = _status['error_skipped']

    @classmethod
    def validate_name(cls, name: str) -> Optional[str]:
        name = to_snakecase(name)
        if name in [to_snakecase(key) for key in cls._status.keys()]:
            return name
        return None

    @classmethod
    def validate_value(cls, value: int | str) -> Optional[int]:
        try:
            value = int(value)
        except ValueError:
            return None
        if value in cls._status.values():
            return value
        return None

    @classmethod
    def get_value(cls, inp: Optional[str | int]) -> int:
        if inp is None:
            return cls.captured
        if isinstance(inp, str):
            name: Optional[str] = cls.validate_name(inp)
            if name:
                return cls._status[name]
        value: Optional[int] = cls.validate_value(inp)
        if value:
            return value
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return cls.captured

    @classmethod
    def get_name(cls, inp: Optional[str | int]) -> str:
        if inp is None:
            return 'Unknown'
        if cls.validate_value(inp) is not None:
            for name, val in cls._status.items():
                if val == inp:
                    return to_title(name)
        if isinstance(inp, str) and cls.validate_name(inp) is not None:
            return to_title(inp)
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return 'Unknown'

    @classmethod
    def get_all_names(cls) -> list[str]:
        return [
            to_title(status)
            for status in cls._status.keys()
        ]


class BaseImage(SQLModel):
    id: UUID = Field(
        default_factory= uuid4,
        primary_key= True,
        index= True,
    )
    extension: str = Field(
        max_length= 10,
        nullable= False,
        default= '.png'
    )
    processed_date: datetime = Field(
        default_factory= lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column= Column(
            DateTime(timezone= False),
            server_default= func.now(),
            nullable= False
        )
    )
    inspection_result: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'inspection_results.name',
        ondelete= 'SET NULL'
    )
    origin: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'origins.name',
        ondelete= 'SET NULL'
    )
    model: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'models.name',
        ondelete= 'SET NULL'
    )
    true_result: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'inspection_results.name',
        ondelete= 'SET NULL'
    )
    trust: Optional[float] = Field(
        default= None,
        nullable= True
    )
    status: int = Field(
        default= ImageStatus.captured,
        nullable= False
    )
    warning: int = Field(
        default= ExtractorsWarnings.NO_WARNING.value,
        nullable= False
    )

    @property
    def file_name(self) -> str:
        return f'{self.id}{self.extension}'

    @property
    def internal_absolute_path(self) -> Path:
        return INTERNAL_IMAGES_FOLDER / self.file_name

    @property
    def external_relative_path(self) -> str:
        return (STATIC_IMAGES_FOLDER / Path(self.file_name)).as_posix()


class Image(BaseImage, table= True):
    __tablename__: str = 'images' # type: ignore

    result_of_image: Optional['InspectionResult'] = Relationship(
        back_populates= 'images_of_result',
        sa_relationship_kwargs=dict(foreign_keys="[Image.inspection_result]")
    )
    true_result_of_image: Optional['InspectionResult'] = Relationship(
        back_populates= 'images_of_true_result',
        sa_relationship_kwargs=dict(foreign_keys="[Image.true_result]")
    )
    origin_of_image: Optional['Origin'] = Relationship(
        back_populates= 'images_of_origin'
    )
    model_of_image: Optional['Model'] = Relationship(
        back_populates= 'images_of_model'
    )


#********** MODEL CLASS **********
class ModelClass(SQLModel, table= True):
    __tablename__: str = 'model_classes' # type: ignore

    model: str = Field(
        primary_key= True,
        foreign_key= 'models.name',
        ondelete= 'CASCADE',
        index= True
    )
    number: int = Field(
        primary_key= True,
        default= 0
    )
    inspection_result: str = Field(
        default= None,
        nullable= True,
        foreign_key= 'inspection_results.name',
        ondelete= 'SET NULL'
    )

    model_of_model_class: Optional['Model'] = Relationship(
        back_populates= 'model_classes_of_model'
    )
    result_of_model_class: Optional['InspectionResult'] = Relationship(
        back_populates= 'model_classes_of_result'
    )


#********** ORIGIN RESULT **********
class OriginResult(SQLModel, table= True):
    __tablename__: str = 'origin_results' # type: ignore

    origin: str = Field(
        primary_key= True,
        foreign_key= 'origins.name',
        ondelete= 'CASCADE',
        index= True
    )
    inspection_result: str = Field(
        primary_key= True,
        foreign_key= 'inspection_results.name',
        ondelete= 'CASCADE',
        index= True
    )
    result: bool = Field(
        default= False,
        nullable= False
    )
    threshold: float = Field(
        default= 0.5,
        nullable= False
    )

    origin_of_origin_result: Optional['Origin'] = Relationship(
        back_populates= 'origin_results_of_origin'
    )
    result_of_origin_result: Optional['InspectionResult'] = Relationship(
        back_populates= 'origin_results_of_result'
    )


#********** ALARM **********
class AlarmTypes(NoInstantiable):
    _status: dict[str, int] = {
        'unknown': 0,
        'info': 1,
        'warning': 2,
        'error': 3,
        'critical': 4,
    }

    unknown: int = _status['unknown']
    info: int = _status['info']
    warning: int = _status['warning']
    error: int = _status['error']
    critical: int = _status['critical']

    @classmethod
    def validate_name(cls, name: str) -> Optional[str]:
        name = to_snakecase(name)
        if name in [to_snakecase(key) for key in cls._status.keys()]:
            return name
        return None

    @classmethod
    def validate_value(cls, value: int | str) -> Optional[int]:
        try:
            value = int(value)
        except ValueError:
            return None
        if value in cls._status.values():
            return value
        return None

    @classmethod
    def get_value(cls, inp: Optional[str | int]) -> int:
        if inp is None:
            return cls.info
        if isinstance(inp, str):
            name: Optional[str] = cls.validate_name(inp)
            if name:
                return cls._status[name]
        value: Optional[int] = cls.validate_value(inp)
        if value:
            return value
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return cls.info

    @classmethod
    def get_name(cls, inp: Optional[str | int]) -> str:
        if inp is None:
            return 'Unknown'
        if cls.validate_value(inp) is not None:
            for name, val in cls._status.items():
                if val == inp:
                    return to_title(name)
        if isinstance(inp, str) and cls.validate_name(inp) is not None:
            return to_title(inp)
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return 'Unknown'

    @classmethod
    def get_all_names(cls) -> list[str]:
        return [
            to_title(status)
            for status in cls._status.keys()
        ]


class Alarm(SQLModel, table= True):
    __tablename__: str = 'alarms' # type: ignore

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    date: datetime = Field(
        default_factory= lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column= Column(
            DateTime(timezone= False),
            server_default= func.now(),
            nullable= False
        )
    )
    origin: Optional[str] = Field(
        default= None,
        nullable= True,
        foreign_key= 'origins.name',
        ondelete= 'SET NULL'
    )
    alarm_type: int = Field(
        default= 0,
        nullable= False,
        index= True
    )
    message: str = Field(
        default= '',
        nullable= False
    )
    
    origin_of_alarm: Optional['Origin'] = Relationship(
        back_populates= 'alarms_of_origin'
    )
