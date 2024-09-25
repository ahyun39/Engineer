## TestClass

테스트 함수를 클래스로 그룹화 할 수 있다.

<br>

`tests/test_class.py`

```python
class TestCalcultor:
    value = 0

    def test_add(self):
        self.value += 1
        assert self.value == 1

    def test_result(self):
        assert self.value == 0
```

<br>

**실행 결과**

- 클래스 내의 각 테스트는 각각의 고유한 클래스 인스턴스를 가지고 있어 self 변수값이 공유되지 않는다.

<p align="center"><img width="380" height="85" alt="Untitled (1)" src="https://github.com/user-attachments/assets/b261f769-8725-40dc-b07b-d08b05e1dcd2"></p>