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


from typing import Optional

from pydantic import BaseModel
from typing_extensions import Self


class ApiIPResponse(BaseModel):
    ip: str


class ImageStreamResponse(BaseModel):
    """Model for broadcast new image"""
    type: str = 'new-image'
    image_url: str
    insp_result: str =  'No result'
    origin: str = 'Unknown'
    true_result: str = 'No result'
    trust: Optional[float] = None

    @classmethod
    def factory(
        cls,
        image_url: str,
        insp_result: Optional[str],
        origin: Optional[str],
        true_result: Optional[str],
        trust: Optional[float]
    ) -> Self:
        return cls(
            image_url= image_url,
            insp_result= insp_result if insp_result is not None else 'No result',
            origin= origin if origin is not None else 'Unknown',
            true_result= true_result if true_result is not None else 'No result',
            trust= trust
        )
