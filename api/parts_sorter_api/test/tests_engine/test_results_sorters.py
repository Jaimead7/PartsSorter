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


from random import randint, random
from typing import Callable

import numpy as np
import pytest
from parts_sorter_api.src.engine.results import (BoxesType, MyBoxes, MyResults,
                                                 ResutlsType, SpeedDict)
from parts_sorter_api.src.engine.results_sorters import (
    RESULTS_SORTERS, ResultsSorterFunction, by_conf, dis_center, no_sort,
    results_sorter_factory)


@pytest.fixture
def speed() -> SpeedDict:
    return SpeedDict(
        preprocess= randint(0, 1000),
        inference= randint(0, 1000),
        postprocess= randint(0, 1000)
    )

@pytest.fixture
def random_boxes() -> BoxesType:
    orig_w: int = 640
    orig_h: int = 640
    orig_shape: tuple[int, int] = (orig_w, orig_h)
    n_classes: int = 10
    boxes_list: list = []
    for _ in range(5):
        x0: int = randint(0, int((orig_w * 0.9) // 1))
        y0: int = randint(0, int((orig_h * 0.9) // 1))
        x1: int = randint(x0, orig_w)
        y1: int = randint(y0, orig_h)
        conf: float = random()
        id: int = randint(0, n_classes - 1)
        boxes_list.append([x0, y0, x1, y1, conf, id])
    boxes_array: np.ndarray = np.array(boxes_list)
    return MyBoxes(
        boxes= boxes_array,
        orig_shape= orig_shape
    )

@pytest.fixture
def random_results(random_boxes: BoxesType, speed: SpeedDict) -> ResutlsType:
    n_classes: int = 10
    names: dict[int, str] = {i: f'Class_{i}' for i in range(n_classes)}
    return MyResults(
        orig_img= np.random.randint(
            0,
            256,
            size=(*random_boxes.orig_shape, 3),
            dtype=np.uint8
        ),
        names= names,
        boxes= random_boxes.data,
        speed= speed
    )

@pytest.fixture
def random_results_no_boxes(speed: SpeedDict) -> ResutlsType:
    n_classes: int = 10
    names: dict[int, str] = {i: f'Class_{i}' for i in range(n_classes)}
    return MyResults(
        orig_img= np.random.randint(
            0,
            256,
            size=(640, 640, 3),
            dtype=np.uint8
        ),
        names= names,
        boxes= None,
        speed= speed
    )


class TestNoSort:
    def test_func(self, random_results: ResutlsType) -> None:
        pre_result: ResutlsType = random_results
        random_results = no_sort(random_results)
        assert pre_result == random_results
        if pre_result.boxes is not None and random_results.boxes is not None:
            assert np.array_equal(
                pre_result.boxes.data,
                random_results.boxes.data
            )

    def test_inplace(self, random_results: ResutlsType) -> None:
        pre_result: ResutlsType = random_results
        no_sort(random_results)
        assert pre_result == random_results
        if pre_result.boxes is not None and random_results.boxes is not None:
            assert np.array_equal(
                pre_result.boxes.data,
                random_results.boxes.data
            )


class TestByConf:
    def test_func(self, random_results: ResutlsType) -> None:
        random_results = by_conf(random_results)
        if random_results.boxes is None:
            return
        conf_list: list = random_results.boxes.data[:, 4].tolist()
        assert conf_list == sorted(conf_list, reverse= True)

    def test_inplace(self, random_results: ResutlsType) -> None:
        by_conf(random_results)
        if random_results.boxes is None:
            return
        conf_list: list = random_results.boxes.data[:, 4].tolist()
        assert conf_list == sorted(conf_list, reverse= True)


class TestDisCenter:
    def test_func(self, speed: SpeedDict) -> None:
        orig_shape = (640, 640)  # (h, w)
        boxes_data: np.ndarray = np.array([
            [380, 300, 420, 340, 0.8, 2],  # Center (400, 320) - distance 80
            [200, 200, 280, 280, 0.7, 3],  # Center (240, 240) - distance 113.14...
            [300, 300, 340, 340, 0.9, 1],  # Center (320, 320) - distance 0
        ])
        boxes: MyBoxes = MyBoxes(
            boxes=boxes_data,
            orig_shape=orig_shape
        )
        results = MyResults(
            orig_img= np.random.randint(0, 255, size=(*orig_shape, 3), dtype=np.uint8),
            names= {1: 'Class_1', 2: 'Class_2', 3: 'Class_3'},
            boxes= boxes.data,
            speed= speed
        )
        sorted_results: ResutlsType = dis_center(results)
        if sorted_results.boxes is not None:
            expected_ids: list[int] = [1, 2, 3]
            actual_ids: list[int] = sorted_results.boxes.data[:, 5].astype(int).tolist()
            assert actual_ids == expected_ids

    def test_inplace(self, speed: SpeedDict) -> None:
        orig_shape = (640, 640)  # (h, w)
        boxes_data: np.ndarray = np.array([
            [380, 300, 420, 340, 0.8, 2],  # Center (400, 320) - distance 80
            [200, 200, 280, 280, 0.7, 3],  # Center (240, 240) - distance 113.14...
            [300, 300, 340, 340, 0.9, 1],  # Center (320, 320) - distance 0
        ])
        boxes: MyBoxes = MyBoxes(
            boxes=boxes_data,
            orig_shape=orig_shape
        )
        results = MyResults(
            orig_img= np.random.randint(0, 255, size=(*orig_shape, 3), dtype=np.uint8),
            names= {1: 'Class_1', 2: 'Class_2', 3: 'Class_3'},
            boxes= boxes.data,
            speed= speed
        )
        dis_center(results)
        if results.boxes is not None:
            expected_ids: list[int] = [1, 2, 3]
            actual_ids: list[int] = results.boxes.data[:, 5].astype(int).tolist()
            assert actual_ids == expected_ids


class TestResultsSorterDictionary:
    def test_all_functions_callable(self, random_results: ResutlsType) -> None:
        for _, func in RESULTS_SORTERS.items():
            assert callable(func)
            try:
                result: ResutlsType = func(random_results)
                assert isinstance(result, ResutlsType)
            except Exception:
                assert False


class TestResultsSorterFactory:
    @pytest.mark.parametrize(
        'name, expected_func',
        [
            ('NONE', no_sort),
            ('CONF', by_conf),
            ('CENTER', dis_center),
        ]
    )
    def test_valid_names_uppercase(self, name: str, expected_func: Callable) -> None:
        func: ResultsSorterFunction = results_sorter_factory(name)
        assert func == expected_func

    @pytest.mark.parametrize(
        'name, expected_func',
        [
            ('none', no_sort),
            ('conf', by_conf),
            ('center', dis_center)
        ]
    )
    def test_valid_names_lowercase(self, name: str, expected_func: Callable) -> None:
        func: ResultsSorterFunction = results_sorter_factory(name)
        assert func == expected_func

    @pytest.mark.parametrize(
        'name, expected_func',
        [
            ('NonE', no_sort),
            ('cOnF', by_conf),
            ('ceNTer', dis_center)
        ]
    )
    def test_valid_names_mixed_case(self, name: str, expected_func: Callable) -> None:
        func: ResultsSorterFunction = results_sorter_factory(name)
        assert func == expected_func

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
        func: ResultsSorterFunction = results_sorter_factory(invalid_name)
        assert func == no_sort


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
