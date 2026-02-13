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


from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional, Protocol
from uuid import UUID

from pydantic import BaseModel, field_validator
from sqlmodel import col, or_
from sqlmodel.sql._expression_select_cls import SelectOfScalar
from typing_extensions import Self

from .database import Image, ImageStatus


class HealthResponse(BaseModel):
    status: str
    service: str


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
    status: list[str] = []

    @field_validator('inspection_results')
    @classmethod
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
    @classmethod
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
    @classmethod
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
    @classmethod
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

    @field_validator('status')
    @classmethod
    def validate_status(
        cls,
        status_names: list[str]
    ) -> list[int]:
        return [
            ImageStatus.get_value(status_name)
            for status_name in status_names
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
        if self.min_trust:
            statement = statement.where(
                col(Image.trust).is_not(None),
            )
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

    def add_status_filter_to_statement(
        self,
        statement: SelectOfScalar[Any]
    ) -> SelectOfScalar[Any]:
        if len(self.status) > 0:
            statement = statement.where(
                col(Image.status).in_(self.status)
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
        statement = self.add_status_filter_to_statement(statement)
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


class ApiResponse(Protocol):
    type: str
    def model_dump(
        self,
        *args: Any,
        mode: Literal['json', 'python'] | str = 'python',
        **kwargs: Any
    ) -> dict[str, Any]: ...


class ImageResponse(BaseModel):
    type: str = 'img'
    id: UUID
    url: str
    insp_result: Optional[str] = 'No result'
    origin: Optional[str] = 'Unknown'
    model: Optional[str] = 'Unknown'
    true_result: Optional[str] = 'No result'
    trust: Optional[float] = 0.
    status: Optional[str | int] = 'Captured'

    @field_validator('insp_result', 'true_result')
    @classmethod
    def validate_no_result(cls, v: Optional[str]) -> str:
        if v is None:
            return 'No result'
        return v

    @field_validator('origin', 'model')
    @classmethod
    def validate_unknown(cls, v: Optional[str]) -> str:
        if v is None:
            return 'Unknown'
        return v

    @field_validator('trust')
    @classmethod
    def validate_float(cls, v: Optional[float]) -> float:
        if v is None:
            return 0.
        return v

    @field_validator('status')
    @classmethod
    def validate_captured(cls, v: Optional[str | int]) -> str:
        if v is None:
            v = ImageStatus.captured
        return ImageStatus.get_name(v)

    @classmethod
    def from_image(
        cls,
        image: Image
    ) -> Self:
        return cls(
            id = image.id,
            url= image.external_relative_path,
            insp_result= image.inspection_result,
            origin= image.origin,
            model= image.model,
            true_result= image.true_result,
            trust= image.trust,
            status= image.status
        )


class ImageProcessedResponse(ImageResponse):
    result: Optional[bool] = True

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: Optional[bool]) -> bool:
        if v is None:
            return True
        return v

    @classmethod
    def from_image(
        cls,
        image: Image,
        result: Optional[bool] = True
    ) -> Self:
        img: Self = super().from_image(image)
        img.result = result
        return img


class ImageHistResponse(ImageResponse):
    index: Optional[int] = 0
    total: Optional[int] = 0

    @field_validator('index', 'total')
    @classmethod
    def validate_int(cls, v: Optional[int]) -> int:
        if v is None:
            return 0
        return v

    @classmethod
    def from_image(
        cls,
        image: Image,
        index: Optional[int] = 0,
        total: Optional[int] = 0
    ) -> Self:
        img: Self = super().from_image(image)
        img.index = index
        img.total = total
        return img


class ImageStatusResponse(BaseModel):
    type: str = 'imgStatus'
    id: UUID
    image_url: str
    status: str = 'Captured'

    @classmethod
    def from_image(
        cls,
        image: Image
    ) -> Self:
        return cls(
            image_url= image.external_relative_path,
            id= image.id,
            status= ImageStatus.get_name(image.status)
        )
