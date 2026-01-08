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


from typing import Callable

import cv2
import numpy as np
import pytest
from parts_sorter_api.src.engine.filters import (IMAGE_FILTERS,
                                                 ImageFilterFunction, bgr2gray,
                                                 bgr2rgb, cut, gray2bgr,
                                                 image_filter_factory,
                                                 no_filter, redim, resize,
                                                 rgb2bgr)


@pytest.fixture
def bgr_image() -> np.ndarray:
    return np.random.randint(0, 256, (100, 150, 3), dtype=np.uint8)


@pytest.fixture
def gray_image() -> np.ndarray:
    return np.random.randint(0, 256, (100, 150), dtype=np.uint8)

@pytest.fixture
def black_bgr_image() -> np.ndarray:
    return np.zeros(shape= (100, 150, 3), dtype=np.uint8)

@pytest.fixture
def black_image() -> np.ndarray:
    return np.zeros(shape= (100, 150), dtype=np.uint8)


class TestNoneFilter:
    def test_returns_same_image_bgr(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = no_filter(bgr_image)
        assert np.array_equal(result, bgr_image)
        assert result.shape == bgr_image.shape
        assert result.dtype == bgr_image.dtype

    def test_returns_same_image_gray(self, gray_image: np.ndarray) -> None:
        result: np.ndarray = no_filter(gray_image)
        assert np.array_equal(result, gray_image)
        assert result.shape == gray_image.shape
        assert result.dtype == gray_image.dtype


class TestResize:
    @pytest.mark.parametrize(
        'width, height',
        [
            (320, 240),
            (640, 640),
            (800, 600),
            (100, 100)
        ]
    )
    def test_bgr_image(self, bgr_image: np.ndarray, width: int, height: int) -> None:
        result: np.ndarray = resize(bgr_image, width=width, height=height)
        assert result.shape == (height, width, 3)

    @pytest.mark.parametrize(
        'width, height',
        [
            (320, 240),
            (640, 640),
            (800, 600),
            (100, 100)
        ]
    )
    def test_gray_image(self, gray_image: np.ndarray, width: int, height: int) -> None:
        result: np.ndarray = resize(gray_image, width=width, height=height)
        assert result.shape == (height, width)
        assert result.dtype == np.uint8

    @pytest.mark.parametrize(
        'width, height',
        [
            (-10, 100),
            (100, -10),
            (0, 100)
        ]
    )
    def test_invalid_sizes(self, bgr_image: np.ndarray, width: int, height: int) -> None:
        try:
            result: np.ndarray = resize(bgr_image, width=width, height=height)
            assert result is not None
        except cv2.error:
            pass


class TestRedim:
    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = redim(bgr_image, width=50, height=50, gray= 100)
        assert result is not None

    #TODO: Complete tests
    ...


class TestGray2Bgr:
    def test_converts_to_bgr(self, gray_image: np.ndarray) -> None:
        result: np.ndarray = gray2bgr(gray_image)
        assert len(result.shape) == 3
        assert result.shape[0] == gray_image.shape[0]
        assert result.shape[1] == gray_image.shape[1]
        assert result.shape[2] == 3
        assert result.dtype == np.uint8

    def test_all_channels_equal(self, gray_image: np.ndarray) -> None:
        result: np.ndarray = gray2bgr(gray_image)
        assert np.array_equal(result[:, :, 0], gray_image)
        assert np.array_equal(result[:, :, 1], gray_image)
        assert np.array_equal(result[:, :, 2], gray_image)

    @pytest.mark.parametrize(
        'shape',
        [
            (100, 100),
            (50, 75),
            (1, 1)
        ]
    )
    def test_various_image_sizes(self, shape: tuple[int]) -> None:
        img: np.ndarray = np.random.randint(0, 256, shape, dtype=np.uint8)
        result: np.ndarray = gray2bgr(img)
        assert result.shape[:2] == shape
        assert result.dtype == np.uint8

    def test_color_image(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = gray2bgr(bgr_image)
        assert np.array_equal(result, bgr_image)
        assert result.shape == bgr_image.shape
        assert result.dtype == bgr_image.dtype


class TestBgr2Gray:
    def test_converts_to_grayscale(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = bgr2gray(bgr_image)
        assert len(result.shape) == 2
        assert result.shape[0] == bgr_image.shape[0]
        assert result.shape[1] == bgr_image.shape[1]
        assert result.dtype == np.uint8

    def test_black_image(self, black_bgr_image: np.ndarray, black_image: np.ndarray) -> None:
        result: np.ndarray = bgr2gray(black_bgr_image)
        assert np.array_equal(result, black_image)
        assert result.shape == black_image.shape
        assert result.dtype == black_image.dtype

    def test_gray_image(self, gray_image: np.ndarray) -> None:
        result: np.ndarray = bgr2gray(gray_image)
        assert np.array_equal(result, gray_image)
        assert result.shape == gray_image.shape
        assert result.dtype == gray_image.dtype

    @pytest.mark.parametrize(
        'shape',
        [
            (100, 100, 3),
            (50, 75, 3),
            (1, 1, 3)
        ]
    )
    def test_various_image_sizes(self, shape: tuple[int]) -> None:
        img: np.ndarray = np.random.randint(0, 256, shape, dtype=np.uint8)
        result: np.ndarray = bgr2gray(img)
        assert result.shape == shape[:2]
        assert result.dtype == np.uint8


class TestBgr2Rgb:
    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = bgr2rgb(bgr_image)
        assert result is not None

    #TODO: Complete tests
    ...


class TestRgb2Bgr:
    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = rgb2bgr(bgr_image)
        assert result is not None

    #TODO: Complete tests
    ...


class TestCut:
    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result = cut(bgr_image, width=50, height=50)
        assert result is not None
        assert np.array_equal(result, bgr_image)

    #TODO: Complete tests
    ...


class TestImageFiltersDictionary:
    def test_all_functions_callable(self, bgr_image: np.ndarray) -> None:
        for _, func in IMAGE_FILTERS.items():
            assert callable(func)
            try:
                result: np.ndarray = func(bgr_image)
                assert isinstance(result, np.ndarray)
            except Exception:
                assert False


class TestImageFilterFactory:
    @pytest.mark.parametrize(
        'name, expected_func',
        [
            ('NONE', no_filter),
            ('RESIZE', resize),
            ('REDIM', redim),
            ('COLOR', gray2bgr),
            ('GRAY', bgr2gray),
            ('RGB', bgr2rgb),
            ('BGR', rgb2bgr),
            ('CUT', cut),
        ]
    )
    def test_valid_names_uppercase(self, name: str, expected_func: Callable) -> None:
        func: ImageFilterFunction = image_filter_factory(name)
        assert func == expected_func

    @pytest.mark.parametrize(
        'name',
        [
            'none',
            'resize',
            'redim',
            'color',
            'gray',
            'rgb',
            'bgr',
            'cut'
        ]
    )
    def test_valid_names_lowercase(self, name: str) -> None:
        func_lower: ImageFilterFunction = image_filter_factory(name)
        func_upper: ImageFilterFunction = image_filter_factory(name.upper())
        assert func_lower == func_upper

    @pytest.mark.parametrize(
        'name',
        [
            'None',
            'Resize',
            'Gray',
            'CoLoR'
        ]
    )
    def test_valid_names_mixed_case(self, name: str) -> None:
        func: ImageFilterFunction = image_filter_factory(name)
        assert func is not None
        assert callable(func)

    @pytest.mark.parametrize(
        'invalid_name',
        [
            'INVALID',
            'RANDOM',
            'FILTER',
            '',
            '123'
        ]
    )
    def test_invalid_names(self, invalid_name: str) -> None:
        func: ImageFilterFunction = image_filter_factory(invalid_name)
        assert func == no_filter


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
