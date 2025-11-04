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
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

import yaml
from sqlalchemy import JSON, Column
#from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel
from typing_extensions import Self

from ..dependencies.config import (EXTERNAL_IMAGES_URL, INTERNAL_IMAGES_FOLDER,
                                   INTERNAL_MODELS_FOLDER)
from .typing import ModelMetadataDict


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
        sa_type= JSON #JSONB  #CHECK: Works ok with postgres?
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
            data: ModelMetadataDict = yaml.safe_load(f)
        return data


#********** IMAGES **********
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

    @property
    def file_name(self) -> str:
        return f'{self.id}{self.extension}'

    @property
    def internal_absolute_path(self) -> Path:
        """Get the complete path of the image file inside the server.
        Returns:
            Path: Path of the image file.
        """
        return INTERNAL_IMAGES_FOLDER / self.file_name

    @property
    def external_url(self) -> str:
        """Get the URL for access the image outside the server.
        Returns:
            str: URL of the image.
        """
        relativePath = Path(self.file_name)
        return EXTERNAL_IMAGES_URL + relativePath.as_posix()


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


class ImageProcessed(BaseImage):
    result: bool = False

    @classmethod
    def factory(
        cls,
        image: Image,
        result: Optional[bool] = None
    ) -> Self:
        return cls(
            id= image.id,
            extension= image.extension,
            processed_date= image.processed_date,
            inspection_result= image.inspection_result,
            origin= image.origin,
            true_result= image.true_result,
            trust= image.trust,
            result= result if result is not None else False
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
