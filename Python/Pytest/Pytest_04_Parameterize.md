## Parameterize

테스트 케이스마다 테스트 값을 포함한 테스트 함수를 호출하는 코드도 중복 작성된다. 테스트 입력 값과 결과 값을 @pytest.mark.parametrize(argnames, argvalues) decorator로 작성하여 테스트 코드를 간결하게 만들 수 있다.

<br>

`tests/test_calculator_parametrize.py`

```python
import pytest

@pytest.mark.parametrize(
    "a, b, result",
    [(1, 2, 3),
     (2, 2, 4)]
)
def test_add(calculator, a, b, result):
    assert calculator.add(a, b) == result

@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 4),
     (2, 2, 6)]
)
def test_add_fail(calculator, a, b, expected):
    assert calculator.add(a, b) != expected
```

<br>

실행 결과

<p align="center"><img width="380" height="90" alt="Untitled (1)" src="https://github.com/user-attachments/assets/65bbc8ca-fd64-4136-bc95-48ec9ffafecd"></p>