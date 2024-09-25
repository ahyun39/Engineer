## skip

테스트 함수를 사용하지 않을 때 @pytest.mark.skip 데코레이터를 사용함으로 테스트를 생략할 수 있다.

다른 사용법으로 테스트가 조건을 만족할 경우 pytest.skip 함수로 skip 처리가 가능하다.

<br>

`tests/test_skip.py`

```python
import pytest

@pytest.mark.skip(reason="no way of currently testing this")
def test_skip_v1():
    assert 1 == 1

def test_skip_v2():
    if True:
        pytest.skip(reason="no way of currently testing this")
    assert 1 == 1
```

<br>

**실행 결과**

<p align="center"><img width="380" height="90" alt="Untitled (1)" src="https://github.com/user-attachments/assets/f9c0ebfb-2366-4567-98d0-fdb8a1198b3e"></p>

- `skipped` : 생략된 테스트 개수

<br>

### skipif

플랫폼이나 라이브러리 설치 유무, 버전 등에 따라 skip이 필요한 경우가 있다.

@pytest.mark.skipif(조건문) 데코레이터로 조건에 부합될 경우에만 테스트 함수를 생략할 수 있다.

<br>

`tests/test_skipif.py`

```python
import pytest
import sys

@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python 3.7 or higher")
def test_skipif_v1():
    assert 1 == 1

try:
    import numpy as np
except ImportError:
    pass

@pytest.mark.skipif('numpy' not in sys.modules, reason="requires the Numpy library")
def test_skipif_v2():
    assert 1 == 1
```

<br>

**실행 결과**

<p align="center"><img width="380" height="90" alt="Untitled (1)" src="https://github.com/user-attachments/assets/6208d946-78af-4a70-a036-14782118eca4"></p>

- test_skipif_v1 : 현재 python 버전이 3.8이므로 생략되지 않고 테스트 실행됨
- test_skipif_v2 : numpy 라이브러리 설치가 되지 않아 ImportError가 발생하고 테스트 생략됨