### django setting

```python
# django project file create
mkdir django-proj

# django project에서 가상환경 설정
cd django-proj
virtualenv venv
source venv/bin/activate

# django install
pip install django
pip freeze # 설치 잘되었는지 확인

# django project 생성
django-admin startproject <project_name>
```

- `/webproj`에 들어가면 [`manage.py`](http://manage.py) 가 있는데 이를 이용해서 서버를 가동

```python
# server 가동
python manage.py runserver
```

<br>

### VS로 webproj 내 파일에 대해 알아보기

```python
__init__.py : webproj라는 directory가 python module로써 인식되게 하는 역할을 담당
asgi.py, wsgi.py : 이후에 서버에서 프로젝트를 진행할 때 다루게 될 부분
settings.py : 전반적인 python django 프로젝트의 설정 사항을 반영하는 file
```

<br>

### django Project and App

<img width="268" alt="Untitled (1)" src="https://github.com/user-attachments/assets/f66dccce-dfd3-4c4b-b04e-e70c77409b8d">

- Naver(Project)
    
    → App (blog), → App (sports), → App(cafe)
    
<br>

### django App 만들기

```python
# django app 생성
django-admin startapp <app_name>
!! 주의
app을 생성할 때는 django-proj내에 있는 webproj 안에서 app 파일을 생성해야한다.

# homepage app 생성
django-admin startapp homepage
```

- VS로 homepage 내 파일에 대해 알아보기
    
    ```python
    admin.py : admin page에 관한 부분
    apps.py : 앱에 대한 설정을 관리
    models.py : homepage라는 module 안에서 쓰일 database의 schema 등등을 이곳에 클래스 형태로 작성해줄 수 있다.
    test.py : project의 test case에 대해서 설명해줄 수 있다.
    views.py : homepage라는 앱에서 view를 어떻게 관리해줄 것인가에 관한 코드를 작성한다.
    ```
    
<br>

### django의 MVT Pattern

<center><img width="346" alt="Untitled (2)" src="https://github.com/user-attachments/assets/7df5f10d-95b6-46a6-af03-9db5692653ea"></center>

**MVT pattern (Model, View, Template)**

- `User` ←request→ `Django` ← `URL`(urls.py) ←`View`(views.py)→`Model` (DB관리) ←→ DB(ORM)
- `User` ←request→ `Django` ← `URL`(urls.py) ←`View`(views.py)→`Template`(Web) .html + template 언어
- 흔히 알고 있는 것. MVC pattern (Model, View, Controller)