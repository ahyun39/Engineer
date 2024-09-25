## 기본 사용법

<br>

### 기본 테스트

`test_sample.py`

```python
# 테스트 대상 기능
def inc(x):
		return x + 1

# 테스트 실행 함수
def test_answer1():
		assert inc(3) == 5

def test_answer2():
		assert inc(3) == 4
```

<br>

**pytest 실행 결과**

- terminal에서 python 파일 생성하기
    - python 파일 생성
        
        ```python
        cat > test_sample.py
        ```
        
    - 파일에 담길 내용 작성
        
        ```python
        # 테스트 대상 기능
        def inc(x):
        		return x + 1
        
        # 테스트 실행 함수
        def test_answer1():
        		assert inc(3) == 5
        
        def test_answer2():
        		assert inc(3) == 4
        ```
        
    - 파일 내용 저장 및 종료
        
        ```python
        control + z
        ```

<br>

- 생성한 파일 내용 확인하기
    - 파일 편집하기
        
        ```python
        vi test_sample.py
        ```
        
    - 저장 및 종료
        
        ```python
        esc 버튼
        
        :wq
        ```

<p align="center"><img width="380" height="180" alt="Untitled (1)" src="https://github.com/user-attachments/assets/e06e9fcb-d02e-4ef3-bd69-f8ca39cbf107"></p>
    

<br>

### 예외 테스트

`test_sample_raises.py`

```python
import pytest

def f():
		raise SystemExit(1)

def test_mytest():
		with pytest.raises(SystemExit):
				f()
```

<p align="center"><img width="380" height="100" alt="Untitled (1)" src="https://github.com/user-attachments/assets/9cfc5040-6ca4-42bc-b8d8-d58b9b785bfb"></p>


<br>

### 명칭 규약

- 파일 이름
    - test_*.py 또는 *_test.py 형식으로 지정한다.
    - *_test.py 는 python 3.8 버전 이상부터 적용된다.
- 클래스 명칭
    - class Test* 형식으로 지정한다.
- 클래스 메서드 및 함수 명칭
    - def test_* 형식으로 지정한다.

<br>

### 실행 방법

- 해당 작업 디렉토리 안에 모든 테스트 파일 실행
    
    ```python
    $ pytest
    ```
    
- 특정 디렉토리 내 테스트 파일 실행
    
    ```python
    $ pytest tests/
    ```
    
- 특정 테스트 파일 실행
    
    ```python
    $ pytest test_sample.py
    ```

<br>   

### 테스트 실행 시 출력되는 정보

- 플랫폼 정보 : python version, pytest library version
- 테스트 실행 디렉토리
- 테스트 파일 이름 및 진행률
- 테스트 실패 파일 및 코드 정보
- 총 테스트 케이스 개수 및 실행시간 정보