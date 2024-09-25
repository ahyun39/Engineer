## 설명문 추가 - id

각 테스트케이스 별로 id를 작성하여 해당 케이스의 의미를 작성할 수 있다.

`tests/test_calculator_param_v3.py`

```python
import pytest

add_test_data = [
    pytest.param(1, 2, 3, id="1 add 2 is 3"),
    pytest.param(2, 2, 4, id="2 add 2 is 4"),
    pytest.param(1, 2, 4, marks=pytest.mark.xfail, id="1 add 2 is not 4"),
    pytest.param(2, 2, 6, marks=pytest.mark.xfail, id="2 add 2 is not 6"),
]

@pytest.mark.parametrize("a, b, result", add_test_data)
def test_add(calculator, a, b, result):
    assert calculator.add(a, b) == result
```