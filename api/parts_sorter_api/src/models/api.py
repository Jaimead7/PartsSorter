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


from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pydantic import BaseModel, field_validator
from sqlmodel import col, or_
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing_extensions import Self

from .database import Image


class HealthResponse(BaseModel):
    status: str
    service: str


class ApiIPResponse(BaseModel):
    ip: str


class ProcessImageResult(BaseModel):
    model_name: Optional[str]
    inpection_result_name: Optional[str]
    trust: Optional[float]


class ImageFilters(BaseModel):
    extensions: list[str] = []
    start_date: Optional[datetime] = datetime.now(timezone.utc) - timedelta(days=30)
    end_date: Optional[datetime] = datetime.now(timezone.utc)
    inspection_results: list[Optional[str]] = []
    origins: list[Optional[str]] = []
    true_results: list[Optional[str]] = []
    min_trust: Optional[float] = 0.
    max_trust: Optional[float] = 1.
    models: list[Optional[str]] = []

    @field_validator('inspection_results')
    def validate_inspection_results(
        cls,
        inspection_results: list[Optional[str]]
    ) -> list[Optional[str]]:
        return [
            None
            if inspection_result == 'No result'
            else inspection_result
            for inspection_result in inspection_results
        ]

    @field_validator('origins')
    def validate_origins(
        cls,
        origins: list[Optional[str]]
    ) -> list[Optional[str]]:
        return [
            None
            if origin == 'Unknown'
            else origin
            for origin in origins
        ]

    @field_validator('true_results')
    def validate_true_results(
        cls,
        true_results: list[Optional[str]]
    ) -> list[Optional[str]]:
        return [
            None
            if true_result == 'No result'
            else true_result
            for true_result in true_results
        ]

    @field_validator('models')
    def validate_models(
        cls,
        models: list[Optional[str]]
    ) -> list[Optional[str]]:
        return [
            None
            if model == 'Unknown'
            else model
            for model in models
        ]

    def add_date_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if self.start_date:
            statement = statement.where(
                col(Image.processed_date) >= self.start_date
            )
        if self.end_date:
            statement = statement.where(
                col(Image.processed_date) <= self.end_date,
            )
        return statement

    def add_trust_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if self.min_trust or self.max_trust:
            statement = statement.where(
                col(Image.trust).is_not(None),
            )
        if self.min_trust:
            statement = statement.where(
                col(Image.trust) >= self.min_trust,
            )
        if self.max_trust:
            statement = statement.where(
                col(Image.trust) <= self.max_trust
            )
        return statement

    def add_extensions_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.extensions) > 0:
            statement = statement.where(
                col(Image.extension).in_(self.extensions)
            )
        return statement

    def add_inspection_result_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.inspection_results) > 0:
            if None in self.inspection_results:
                statement = statement.where(
                    or_(
                        col(Image.inspection_result).in_(self.inspection_results),
                        col(Image.inspection_result).is_(None)
                    )
                )
            else:
                statement = statement.where(
                    col(Image.inspection_result).in_(self.inspection_results)
                )
        return statement

    def add_origins_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.origins) > 0:
            if None in self.origins:
                statement = statement.where(
                    or_(
                        col(Image.origin).in_(self.origins),
                        col(Image.origin).is_(None)
                    )
                )
            else:
                statement = statement.where(
                    col(Image.origin).in_(self.origins)
                )
        return statement

    def add_models_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.models) > 0:
            if None in self.models:
                statement = statement.where(
                    or_(
                        col(Image.model).in_(self.models),
                        col(Image.model).is_(None)
                    )
                )
            else:
                statement = statement.where(
                    col(Image.model).in_(self.models)
                )
        return statement

    def add_true_results_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.true_results) > 0:
            if None in self.true_results:
                statement = statement.where(
                    or_(
                        col(Image.true_result).in_(self.true_results),
                        col(Image.true_result).is_(None)
                    )
                )
            else:
                statement = statement.where(
                    col(Image.true_result).in_(self.true_results)
                )
        return statement

    def add_filters_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        statement = self.add_date_filter_to_statement(statement)
        statement = self.add_trust_filter_to_statement(statement)
        statement = self.add_extensions_filter_to_statement(statement)
        statement = self.add_inspection_result_filter_to_statement(statement)
        statement = self.add_origins_filter_to_statement(statement)
        statement = self.add_models_filter_to_statement(statement)
        statement = self.add_true_results_filter_to_statement(statement)
        return statement


class CameraParams(BaseModel):
    camera_width: int = 640
    camera_height: int = 480
    brightness: float = 128.0
    contrast: float = 32.0
    saturation: float = 32.0
    exposure: float = 40.0
    auto_exposure: int = 3
    wb: float = 0.0
    auto_wb: int = 1

    @classmethod
    def from_dict(
        cls,
        params: Optional[dict[str, Any]]
    ) -> Self:
        if params is None:
            params = {}
        return cls(**params)


class ImageStreamResponse(BaseModel):
    type: str = 'new-image'
    image_url: str
    insp_result: str = 'No result'
    origin: str = 'Unknown'
    model: str = 'Unknown'
    true_result: str = 'No result'
    trust: Optional[float] = None

    @classmethod
    def factory(
        cls,
        image_url: str,
        insp_result: Optional[str],
        origin: Optional[str],
        model: Optional[str],
        true_result: Optional[str],
        trust: Optional[float]
    ) -> Self:
        return cls(
            image_url= image_url,
            insp_result= insp_result if insp_result is not None else 'No result',
            origin= origin if origin is not None else 'Unknown',
            model= model if model is not None else 'Unknown',
            true_result= true_result if true_result is not None else 'No result',
            trust= trust
        )

    @classmethod
    def from_image(
        cls,
        image: Image
    ) -> Self:
        return cls.factory(
            image_url= image.external_relative_path,
            insp_result= image.inspection_result,
            origin= image.origin,
            model= image.model,
            true_result= image.true_result,
            trust= image.trust
        )


class ImageHistResponse(ImageStreamResponse):
    index: int = 0
    total: int = 0

    @classmethod
    def factory(
        cls,
        image_url: str,
        insp_result: Optional[str],
        origin: Optional[str],
        model: Optional[str],
        true_result: Optional[str],
        trust: Optional[float],
        index: Optional[int] = None,
        total: Optional[int] = None
    ) -> Self:
        return cls(
            image_url= image_url,
            insp_result= insp_result if insp_result is not None else 'No result',
            origin= origin if origin is not None else 'Unknown',
            model= model if model is not None else 'Unknown',
            true_result= true_result if true_result is not None else 'No result',
            trust= trust,
            index= index if index is not None else 0,
            total= total if total is not None else 0
        )

    @classmethod
    def from_image(
        cls,
        image: Image,
        index: Optional[int] = None,
        total: Optional[int] = None
    ) -> Self:
        return cls.factory(
            image_url= image.external_relative_path,
            insp_result= image.inspection_result,
            origin= image.origin,
            model= image.model,
            true_result= image.true_result,
            trust= image.trust,
            index= index,
            total= total
        )
