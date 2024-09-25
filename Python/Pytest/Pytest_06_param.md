## param

pytest.param 을 사용하여 테스트 케이스별로 옵션을 지정할 수 있다.

<br>

`tests/test_calculator_param_v1.py`

```python
import pytest

@pytest.mark.parametrize(
    "a, b, expected",
    [pytest.param(1, 2, 4, marks=pytest.mark.xfail),
     pytest.param(2, 2, 6, marks=pytest.mark.xfail)]
)
def test_add_fail_xfail(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

<br>

### 성공/실패 케이스 통합

pytest.param xfail로 하나의 테스트 함수에서 성공과 실패 케이스 모두 테스트할 수 있다.

`tests/test_calculator_param_v2.py`

```python
import pytest

@pytest.mark.parametrize(
    "a, b, result",
    [(1, 2, 3),
     (2, 2, 4),
     pytest.param(1, 2, 4, marks=pytest.mark.xfail),
     pytest.param(2, 2, 6, marks=pytest.mark.xfail)]
)
def test_add(calculator, a, b, result):
    assert calculator.add(a, b) == result
```

<br>

### 테스트케이스 전역변수

가독성 및 재사용성을 위해 테스트케이스를 별도의 변수로 지정하여 사용할 수 있다.

`tests/test_calculator_param_v3.py`

```python
import pytest

add_test_data = [
    (1, 2, 3),
    (2, 2, 4),
    pytest.param(1, 2, 4, marks=pytest.mark.xfail),
    pytest.param(2, 2, 6, marks=pytest.mark.xfail),
]

@pytest.mark.parametrize("a, b, result", add_test_data)
def test_add(calculator, a, b, result):
    assert calculator.add(a, b) == result
```