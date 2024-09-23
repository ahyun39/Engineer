### Model로 DB 구성하기

<br>

**데이터베이스 (구조화)**

- Relational DB (테이블 형식으로) → row(record), column(attribute)
- pandas df 와 완전히 유사하다.
    - max(), groupby() apply 가능
- SQL

<br>

**ORM Object → 객체**

- django에 내장되어 있다.

```python
models.py
```

```python
# models.py
## model을 만들 때 class 단위로 만들 수 있다.

class <모델 이름>(models.Model):
		field1 = models.FieldType(option 추가 가능)...# Field 1 _field의 type을 정할 수 있다.
		field2 = models.FieldType()...# Field 2
		"""
		문자열 : CharField
		숫자 : IntegerField, SmallIntegerField,...
		논리형 : BooleanField
		시간/날짜 : DateTimeField
		...
		"""
		filed option 찾아보기

class Coffee(models.Model):
		name = models.CharField(default="",max_length=30)
		price = models.IntegerField(default=0)
		is_ice = models.BooleanField(default=False)
```

```python
# admin.py
##  어떤 모델이 있을 때 이를 자연스럽게 관리할 수 있다.

from .models import Coffee # admin.py에서 Coffee를 사용할 수 있다.

admin.site.register(Coffee)
```

<br>

> <ins>**models.py**, **admin.py**</ins> **작성 후 http…/admin/에 접속하게 되면 다음과 같이 출력된다.**

<br>

<center><img width="400" height="150" alt="Untitled" src="https://github.com/user-attachments/assets/9ea7450b-cbfd-4d54-8bb5-4dc41c7927a2"></center>

<br>

→ `Coffees`를 누르면 아래와 같이 오류가 발생하게 된다.

<center><img width="400" height="200" alt="Untitled (1)" src="https://github.com/user-attachments/assets/a5035908-5c26-472d-85ce-a3054fa6e98c"></center>

→ DB의 관점에서 DB에 어떤 변동 사항이 생기면 이 변동사항을 <ins>**settings.py**</ins>에서 반영을 해줘야 한다.

<br>

> **위에서 발생한 no such table을 해결하기 위해서는 아래의 작업이 필요하다.**

```python
django-proj/webproj > python manage.py makemigrations homepage
```

<img width="450" height="80" alt="Untitled (6)" src="https://github.com/user-attachments/assets/3c1fee67-12d4-4221-b279-df2b13f57efd">

<br>

```python
# 만들어진 migration을 데이터에 반영
django-proj/webproj > python manage.py migrate
```

<img width="450" height="100" alt="Untitled (7)" src="https://github.com/user-attachments/assets/ea9eecbd-2789-411d-9690-7029b23ba41b">

⇒ 관계형 데이터베이스가 만들어지는 구조가 된다.

<br>

> migrate 실행 후 admin의 Coffees를 들어가게 되면 아래와 같이
**<ins>model.py</ins> 에서 작성했던 부분들을 볼 수 있게 된다.**
> 

<img width="500" height="200" alt="Untitled (8)" src="https://github.com/user-attachments/assets/2bb5cf13-e3fd-4acb-8d1f-05379bc6dcfc">

→ Add coffee를 통해 2개의 Object를 추가한 후 아래와 같이 저장된 것을 확인할 수 있다.

<br>

<img width="300" height="150" alt="Untitled (9)" src="https://github.com/user-attachments/assets/faf9b2da-7da1-4603-bc81-8e32c7b8de3f">

<br>

> **Coffee object (1), (2) 라고 나와있어서 어떤 것인지 알기에 어려움이 있다.**

```python
# models.py
class Coffee(models.Model):
		def __str__(self): # Coffee 객체를 출력하는 과정에서 어떤 문자열을 보여줄 지 결정하는 함수이다.
			return self.name # Coffee 객체를 대표하는 self.name이 출력될 수 있게 한다.
		name = ...
		...
```

<img width="400" height="200" alt="Untitled (10)" src="https://github.com/user-attachments/assets/963fcf39-a39a-4af4-a3b4-72e2beaa917e">

→ object가 아닌 name으로 출력되어 보기 편해졌다.

<br>
<br>
<br>

### <span style="color:Maroon">django Error : That port is already in use</span>

<br>

> 갑자기 오류를 맞이하게 됐다…

<img width="500" height="80" alt="Untitled (11)" src="https://github.com/user-attachments/assets/9dfd1e3b-c927-4aaa-b067-18f679d0c023">

<br>

> 해결
>>
>> lsof -i:8000
>>
>> <img width="500" height="50" alt="Untitled (12)" src="https://github.com/user-attachments/assets/11cd9a05-7d82-4831-b0d7-da58c60e6a9a">
>> 
>> <br>
>>
>> kill -9 [PID]
>>
>> lsof -i:8000  # 다시 확인해본다.
>>
>> python <ins>**manage.py**</ins> runserver # 해결완료
>>
> 혹시 다른 서비스가 이미 8000번 포트를 사용하고 있다면
> 
>>
>> python <ins>**manage.py**</ins> runserver 0.0.0.0:8001