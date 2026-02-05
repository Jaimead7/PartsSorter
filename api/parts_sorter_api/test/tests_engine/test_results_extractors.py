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

import numpy as np
import pytest
from parts_sorter_api.src.engine.results import (BoxesType, MyBoxes, MyResults,
                                                 ResultsType, SpeedDict)
from parts_sorter_api.src.engine.results_extractors import (
    ClassResult, ResultsExtractorFunction, ResultsExtractorRegistry,
    extract_first_result)


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
def random_results(random_boxes: BoxesType, speed: SpeedDict) -> ResultsType:
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


class TestClassResult:
    def test_default(self) -> None:
        res: ClassResult = ClassResult()
        assert res.id == None
        assert res.trust == None

    def test_validate_id(self) -> None:
        assert ClassResult(id= 0).id == 0
        assert ClassResult(id= 1).id == 1
        assert ClassResult(id= '1').id == 1  #type: ignore
        with pytest.raises(ValueError):
            _ = ClassResult(id= -1)
        with pytest.raises(ValueError):
            _ = ClassResult(id= 'test')  #type: ignore

    def test_validate_trust(self) -> None:
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


class TestResultsSorterRegistry:
    def test_no_instance(self) -> None:
        with pytest.raises(SyntaxError):
            _ = ResultsExtractorRegistry()

    def test_null_factory(self) -> None:
        func: ResultsExtractorFunction = ResultsExtractorRegistry.get('None')
        assert func == ResultsExtractorRegistry.no_extract

    def test_no_extract(self, random_results: ResultsType) -> None:
        result: ClassResult = ResultsExtractorRegistry.no_extract(random_results)
        assert result.id == None
        assert result.trust == None

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

    def test_func(self, random_results: ResultsType) -> None:
        result: ClassResult = extract_first_result(random_results)
        if random_results.boxes is None:
            return
        id: int = random_results.boxes.data[0, -1]
        trust: int = random_results.boxes.data[0, -2]
        assert result.id == id
        assert result.trust == trust


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
