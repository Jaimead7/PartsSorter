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
        'pushed': 1,
        'left': 2,
        'lost': 3
    }

    captured: int = _status['captured']
    pushed: int = _status['pushed']
    left: int = _status['left']
    lost: int = _status['lost']

    @classmethod
    def validate_name(cls, name: str) -> bool:
        if name.lower() in [key.lower() for key in cls._status.keys()]:
            return True
        return False

    @classmethod
    def validate_value(cls, value: int) -> bool:
        if value in cls._status.values():
            return True
        return False

    @classmethod
    def get_value(cls, inp: str | int) -> int:
        if isinstance(inp, str):
            try:
                inp = int(inp)
            except ValueError:
                if cls.validate_name(inp):
                    return cls._status[inp.lower()]
        if isinstance(inp, int) and cls.validate_value(inp):
            return inp
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return cls.captured

    @classmethod
    def get_name(cls, inp: str | int) -> str:
        if isinstance(inp, int) and cls.validate_value(inp):
            for name, val in cls._status.items():
                if val == inp:
                    return name.capitalize()
        if isinstance(inp, str) and cls.validate_name(inp):
            return inp.capitalize()
        my_logger.warning(f'"{inp}" is not in {cls.__name__}.')
        return 'Not found'


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
    processed_date: Optional[datetime] = Field(
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
