## xfail

@pytest.mark.xfail 은 테스트 실패가 예상되는 함수에 지정하는 데코레이터이다.

- reason parameter : 작성자가 실패가 되는 이유를 작성하는 부분

<br>

`tests/test_calculator_xfail_v1.py`

```python
import pytest

@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 4),
     (2, 2, 6)]
)
def test_add_fail_parametrize(calculator, a, b, expected):
    assert calculator.add(a, b) != expected

@pytest.mark.xfail(reason="wrong result")
@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 4),
     (2, 2, 6),
     (3, 4, 7)]
)
def test_add_fail_xfail(calculator, a, b, expected):
    assert calculator.add(a, b) == expected
```

<br>

**실행 결과**

<p align="center"><img width="380" height="85" alt="Untitled (1)" src="https://github.com/user-attachments/assets/1502bac1-0372-46db-b4ee-9c390b91889c"></p>

- `passed` : 에러없이 테스트케이스 통과한 개수
- `xfailed` : xfail로 지정한 테스트케이스 중 정상적으로 실패한 개수
- `xpassed` : xfail로 지정한 테스트케이스 중 의도하지 않게 성공한 개수