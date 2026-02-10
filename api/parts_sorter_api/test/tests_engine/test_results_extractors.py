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


from random import randint, random
from typing import Any, Optional

import numpy as np
import pytest
from parts_sorter_api.src.engine.results import (BoxesType, MyBoxes, MyResults,
                                                 ResultsType, SpeedDict)
from parts_sorter_api.src.engine.results_extractors import (
    ClassResult, ClassResultErrors, ResultsExtractorFunction,
    ResultsExtractorRegistry, extract_first_result, extract_first_result_alone)


@pytest.fixture
def n_classes() -> int:
    return 10

@pytest.fixture
def names(n_classes: int) -> dict[int, str]:
    return {i: f'Class_{i}' for i in range(n_classes)}

@pytest.fixture
def speed() -> SpeedDict:
    return SpeedDict(
        preprocess= randint(0, 1000),
        inference= randint(0, 1000),
        postprocess= randint(0, 1000)
    )

@pytest.fixture
def org_img() -> np.ndarray:
    orig_w: int = 640
    orig_h: int = 640
    return np.random.randint(
        0,
        256,
        size=(orig_h, orig_w, 3),
        dtype=np.uint8
    )

@pytest.fixture
def random_boxes(org_img: np.ndarray, n_classes: int) -> BoxesType:
    orig_w: int = org_img.shape[1]
    orig_h: int = org_img.shape[0]
    orig_shape: tuple[int, int] = (orig_w, orig_h)
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
def random_results(
    random_boxes: BoxesType,
    org_img: np.ndarray,
    speed: SpeedDict,
    names: dict[int, str]
) -> ResultsType:
    return MyResults(
        orig_img= org_img,
        names= names,
        boxes= random_boxes.data,
        speed= speed
    )

@pytest.fixture
def one_result(
    random_boxes: BoxesType,
    org_img: np.ndarray,
    speed: SpeedDict,
    names: dict[int, str]
) -> ResultsType:
    return MyResults(
        orig_img= org_img,
        names= names,
        boxes= random_boxes.data[0:1],
        speed= speed
    )

@pytest.fixture
def empty_result(
    org_img: np.ndarray,
    speed: SpeedDict,
    names: dict[int, str]
) -> ResultsType:
    return MyResults(
        orig_img= org_img,
        names= names,
        boxes= None,
        speed= speed
    )


class TestClassResultErrors:
    @pytest.mark.parametrize(
        'value',
        [
            ('error'),
            (0),
            (1),
        ]
    )
    def test_validate_errors(self, value: Any) -> None:
        assert not ClassResultErrors.validate(value)


class TestClassResult:
    def test_default(self) -> None:
        res: ClassResult = ClassResult()
        assert res.id is None
        assert res.trust is None

    def test_validate_id(self) -> None:
        assert ClassResult(id= None).id is None
        assert ClassResult(id= 0).id == 0
        assert ClassResult(id= 1).id == 1
        assert ClassResult(id= '1').id == 1  #type: ignore
        assert ClassResult(id= -1).id == -1
        with pytest.raises(ValueError):
            _ = ClassResult(id= 'test')  #type: ignore

    def test_validate_trust(self) -> None:
        assert ClassResult(trust= None).trust is None
        assert ClassResult(trust= 0.).trust == 0
        assert ClassResult(trust= 1.).trust == 1
        assert ClassResult(trust= 0.5).trust == 0.5
        assert ClassResult(trust= '0.5').trust == 0.5  #type: ignore
        with pytest.raises(ValueError):
            _ = ClassResult(trust= -0.1)
        with pytest.raises(ValueError):
            _ = ClassResult(trust= 1.1)  #type: ignore
        with pytest.raises(ValueError):
            _ = ClassResult(trust= 'test')  #type: ignore

    def test_unpack(self) -> None:
        id: Optional[int]
        trust: Optional[float]
        id, trust = ClassResult(id= 1, trust= 0.5).unpack()
        assert id == 1
        assert trust == 0.5


class TestResultsSorterRegistry:
    def test_no_instance(self) -> None:
        with pytest.raises(SyntaxError):
            _ = ResultsExtractorRegistry()

    def test_null_factory(self) -> None:
        func: ResultsExtractorFunction = ResultsExtractorRegistry.get('None')
        assert func == ResultsExtractorRegistry.no_extract

    def test_no_extract(self, random_results: ResultsType) -> None:
        result: ClassResult = ResultsExtractorRegistry.no_extract(random_results)
        assert result.id is None
        assert result.trust is None

    def test_register(self) -> None:
        try:
            @ResultsExtractorRegistry.register('test')
            def fnc(results: ResultsType) -> ClassResult:
                return ClassResult()
            assert ResultsExtractorRegistry.get('test') == fnc
            assert 'TEST' in ResultsExtractorRegistry.list()
        finally:
            ResultsExtractorRegistry.unregister('test')
        assert 'TEST' not in ResultsExtractorRegistry.list()

    def test_clear_register(self) -> None:
        temp: dict[str, ResultsExtractorFunction] = ResultsExtractorRegistry._extractors.copy()
        try:
            @ResultsExtractorRegistry.register('test')
            def fnc(results: ResultsType) -> ClassResult:
                return ClassResult()
            ResultsExtractorRegistry.clear()
            assert ResultsExtractorRegistry._extractors == {}
        finally:
            ResultsExtractorRegistry._extractors = temp


class TestExtractFirstResult:
    @pytest.mark.parametrize(
        'name',
        [
            ('FIRST'),
            ('first'),
            ('FirST'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ResultsExtractorFunction = ResultsExtractorRegistry.get(name)
        assert func == extract_first_result

    def test_empty(self, empty_result: ResultsType) -> None:
        result: ClassResult = extract_first_result(empty_result)
        assert result.id is None
        assert result.trust is None

    def test_one_result(self, one_result: ResultsType) -> None:
        result: ClassResult = extract_first_result(one_result)
        if one_result.boxes is None:
            return
        assert result.id == one_result.boxes.data[0, -1]
        assert result.trust == one_result.boxes.data[0, -2]

    def test_random_results(self, random_results: ResultsType) -> None:
        result: ClassResult = extract_first_result(random_results)
        if random_results.boxes is None:
            return
        assert result.id == random_results.boxes.data[0, -1]
        assert result.trust == random_results.boxes.data[0, -2]


class TestExtractFirsResultAlone:
    @pytest.mark.parametrize(
        'name',
        [
            ('ALONE'),
            ('alone'),
            ('aLOnE'),
        ]
    )
    def test_factory(self, name: str) -> None:
        func: ResultsExtractorFunction = ResultsExtractorRegistry.get(name)
        assert func == extract_first_result_alone

    def test_empty(self, empty_result: ResultsType) -> None:
        result: ClassResult = extract_first_result_alone(empty_result)
        assert result.id is None
        assert result.trust is None

    def test_one_result(self, one_result: ResultsType) -> None:
        result: ClassResult = extract_first_result_alone(one_result)
        if one_result.boxes is None:
            return
        assert result.id == one_result.boxes.data[0, -1]
        assert result.trust == one_result.boxes.data[0, -2]

    def test_random_results(self, random_results: ResultsType) -> None:
        result: ClassResult = extract_first_result(random_results)
        if random_results.boxes is None:
            return
        assert result.id == random_results.boxes.data[0, -1]
        assert result.trust == random_results.boxes.data[0, -2]

    def test_no_overlap_far_away(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [100, 100, 150, 150, 0.9, 1],     # Base box
            [200, 200, 250, 250, 0.8, 2],     # Far away
            [300, 300, 350, 350, 0.7, 3]      # Far away
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == 1
        assert output.trust == 0.9

    def test_direct_overlap(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [100, 100, 150, 150, 0.9, 1],     # Base box
            [120, 120, 140, 140, 0.8, 2]      # Inside base box
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == ClassResultErrors.OVERLAP.value
        assert output.trust is None

    def test_threshold_proximity_overlap(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [100, 100, 150, 150, 0.9, 1],     # Base box
            [160, 100, 170, 150, 0.8, 2]      # xmin = 160, base_xmax = 150 + 10 = 160
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == 1
        assert output.trust == 0.9

    def test_within_threshold_range(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [100, 100, 150, 150, 0.9, 1],     # Base box
            [155, 100, 165, 150, 0.8, 2]      # 5 pixels away (within threshold)
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == ClassResultErrors.CLOSE.value
        assert output.trust is None

    def test_reversed_coordinates(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [150, 150, 100, 100, 0.9, 1],     # Reversed: x0 > x1, y0 > y1
            [120, 120, 140, 140, 0.8, 2]      # Inside (should trigger overlap)
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == ClassResultErrors.OVERLAP.value
        assert output.trust is None

    def test_multiple_overlaps(
        self,
        org_img: np.ndarray,
        speed: SpeedDict,
        names: dict[int, str]
    ) -> None:
        boxes: np.ndarray = np.array([
            [100, 100, 150, 150, 0.9, 1],     # Base box
            [200, 200, 250, 250, 0.8, 2],     # Far away (no overlap)
            [120, 120, 140, 140, 0.7, 3]      # Overlap (should trigger failure)
        ])
        results: ResultsType = MyResults(
            orig_img= org_img,
            names= names,
            boxes= boxes,
            speed= speed
        )
        output: ClassResult = extract_first_result_alone(results)
        assert output.id == ClassResultErrors.OVERLAP.value
        assert output.trust is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
