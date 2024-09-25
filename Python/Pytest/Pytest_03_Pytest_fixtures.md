## pytest fixtures

<br>

**fixtures?**

- 테스트 프로세스를 초기화하여 시스템의 모든 전제 조건을 충족하도록 시스템을 설정하는 것.
    - 데이터베이스 등
- 같은 설정의 테스트를 쉽게 반복적으로 수행할 수 있도록 도와주는 것.

pytest fixtures 는 python decorator 형식으로 사용한다.

<br>

`src/calculator.py`

```python
class Calculator():
    def add(self, x, y):
        return x + y

    def sub(self, x, y):
        return x - y

    def mul(self, x, y):
        return x * y

    def div(self, x, y):
        return x / y
```

<br>

`test/test_calculator.py`

```python
import pytest

from src.calculator import Calculator

def test_add():
    calculator = Calculator()
    assert calculator.add(1, 2) == 3
    assert calculator.add(2, 2) == 4

def test_sub():
    calculator = Calculator()
    assert calculator.sub(5, 1) == 4
    assert calculator.sub(3, 2) == 1

def test_mul():
    calculator = Calculator()
    assert calculator.mul(2, 2) == 4
    assert calculator.mul(5, 6) == 30

def test_div():
    calculator = Calculator()
    assert calculator.div(8, 2) == 4
    assert calculator.div(9, 3) == 3
```

<br>

### @pytest.fixture

테스트 코드를 작성하다 보면 클래스 호출 등 테스트에 반복 사용되는 코드가 존재한다. 이러한 코드 중복성을 문제를 해결하기 위한 테스트 함수 실행 전 실행되는 함수를 @pytest.fixtrue decorator 로 선언한다.

<br>

`tests/test_calculator_fixture_v1.py`

```python
import pytest

from src.calculator import Calculator

@pytest.fixture
def calculator():
    calculator = Calculator()
    return calculator

def test_add(calculator):
    assert calculator.add(1, 2) == 3
    assert calculator.add(2, 2) == 4

def test_sub(calculator):
    assert calculator.sub(5, 1) == 4
    assert calculator.sub(3, 2) == 1
...
```

사전에 fixture 함수를 정의하고 test_* 함수의 파라미터로 사용하여 클래스 선언 등의 초기화를 진행할 수 있다.

<br>
<br>

### conftest.py

conftest.py에 fixture 코드들을 선언하여 모든 테스트 코드에서는 해당 fixture를 공유하여 사용한다.

<br>

`tests/conftest.py`

```python
import pytest

from src.calculator import Calculator

@pytest.fixture
def calculator():
    calculator = Calculator()
    return calculator
```

<br>

`tests/test_calculator_fixture_v2.py`

```python
def test_add(calculator):
    assert calculator.add(1, 2) == 3
    assert calculator.add(2, 2) == 4

def test_sub(calculator):
    assert calculator.sub(5, 1) == 4
    assert calculator.sub(3, 2) == 1
...
```