## 테스트 디렉토리 구조

- 프로젝트의 효율적인 관리를 위해 소스코드, 테스트 코드 파일을 분리하여 저장한다.
- 테스트 코드는 보통 `tests/` 디렉토리에서 관리한다.

<br>

```python
project/
	src/
			__init__.py
			calculator.py
	tests/
			__init__.py
			test_calculator.py
```

- python 디렉토리 안에 `__init__.py` 파일이 없을 경우, ModuleNotFoundError 에러가 발생할 수 있다.