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


import cv2
import numpy as np
import pytest
from parts_sorter_api.src.engine.filters import (ImageFilterFunction,
                                                 ImageFilterRegistry, bgr2gray,
                                                 bgr2rgb, cut, gray2bgr, redim,
                                                 resize, rgb2bgr)


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


class TestImageFilterRegistry:
    def test_no_instance(self) -> None:
        with pytest.raises(SyntaxError):
            _ = ImageFilterRegistry()

    def test_null_factory(self) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get('None')
        assert func == ImageFilterRegistry.no_filter

    @pytest.mark.parametrize(
        'img_name',
        [
            'bgr_image',
            'gray_image',
            'black_bgr_image',
            'black_image'
        ]
    )
    def test_no_filter(self, request: pytest.FixtureRequest, img_name: str) -> None:
        img: np.ndarray = request.getfixturevalue(img_name)
        result: np.ndarray = ImageFilterRegistry.no_filter(img)
        assert np.array_equal(result, img)
        assert result.shape == img.shape
        assert result.dtype == img.dtype

    def test_register(self) -> None:
        try:
            @ImageFilterRegistry.register('test')
            def fnc(img: np.ndarray) -> np.ndarray:
                return img
            assert ImageFilterRegistry.get('test') == fnc
            assert 'TEST' in ImageFilterRegistry.list()
        finally:
            ImageFilterRegistry.unregister('test')
        assert 'TEST' not in ImageFilterRegistry.list()

    def test_clear_register(self) -> None:
        temp: dict[str, ImageFilterFunction] = ImageFilterRegistry._filters.copy()
        try:
            @ImageFilterRegistry.register('test')
            def fnc(img: np.ndarray) -> np.ndarray:
                return img
            ImageFilterRegistry.clear()
            assert ImageFilterRegistry._filters == {}
        finally:
            ImageFilterRegistry._filters = temp


class TestResize:
    @pytest.mark.parametrize(
        'name',
        [
            ('RESIZE'),
            ('resize'),
            ('rEsIZe'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == resize

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
    @pytest.mark.parametrize(
        'name',
        [
            ('REDIM'),
            ('redim'),
            ('REdim'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == redim

    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = redim(bgr_image, width=50, height=50, gray= 100)
        assert result is not None

    #TODO: Complete tests
    ...


class TestGray2Bgr:
    @pytest.mark.parametrize(
        'name',
        [
            ('COLOR'),
            ('color'),
            ('cOLoR'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == gray2bgr

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
    @pytest.mark.parametrize(
        'name',
        [
            ('GRAY'),
            ('gray'),
            ('grAY'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == bgr2gray

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
    @pytest.mark.parametrize(
        'name',
        [
            ('RGB'),
            ('rgb'),
            ('RgB'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == bgr2rgb

    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = bgr2rgb(bgr_image)
        assert result is not None

    #TODO: Complete tests
    ...


class TestRgb2Bgr:
    @pytest.mark.parametrize(
        'name',
        [
            ('BGR'),
            ('bgr'),
            ('bGr'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == rgb2bgr

    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = rgb2bgr(bgr_image)
        assert result is not None

    #TODO: Complete tests
    ...


class TestCut:
    @pytest.mark.parametrize(
        'name',
        [
            ('CUT'),
            ('cut'),
            ('Cut'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ImageFilterFunction = ImageFilterRegistry.get(name)
        assert func == cut

    def test_function_exists(self, bgr_image: np.ndarray) -> None:
        result: np.ndarray = cut(bgr_image, width=50, height=50)
        assert result is not None
        assert np.array_equal(result, bgr_image)

    #TODO: Complete tests
    ...


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
