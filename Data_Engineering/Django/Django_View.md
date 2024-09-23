### View로 Request Handling하기

- View
    
    ```python
    # homepage -> views.py
    from django.shortcuts import HttpResponse, render
    
    def index(request):
        return HttpResponse("Hello World")
    --------------------------------------------------
    # webproj -> urls.py
    
    from django.contrib import admin
    from django.urls import path
    # url과 views.py는 다른 경로에 있는 파일이기 때문에
    # from homepage.views를 통해 함수를 import 한다.
    from homepage.views import index # views.py에 작성했던 index 함수
    
    urlpatterns = [
    		path('',index) # 127.0.0.1/
    ]
    --------------------------------------------------
    # webproj -> settings.py
    
    INSTALLED_APPS = [
    		"homepage" # homepage app을 반드시 추가해줘야한다.
    ]
    ```
    
- run
    
    ```python
    python manage.py runserver
    ```
    
    위 code로 실행 후, 주소로 들어가면 Hello World를 출력
    
    <img width="300" height="200" alt="Untitled" src="https://github.com/user-attachments/assets/79b0b271-5503-4fa9-8521-fd2a8b05907c" >

<br>
<br>

### path(”admin/”)

127.0.0.1/admin 에 접속

 <img width="300" height="200" alt="Untitled (1)" src="https://github.com/user-attachments/assets/b641dd9c-5ab9-4eb1-b9ae-84a9fbeb7c7d">

    - 우리가 만든 앱의 관리자 페이지에 접근할 수 있다.

<br>

**로그인을 하게 되면**

- 만든 앱에 대한 전반적인 관리 (DB관리 등)

<br>

**로그인을 하기 위해 계정 생성 필요**

- 관리자 user 만들기
    
    ```python
    ~/django-proj/webproj > python manage.py createsuperuser
    # ERROR
    # 우리가 처음 django app을 만들 때 admin이라는 database가 자동적으로 생성된다.
    # 이 DB에 대한 정보를 migration을 진행해줘야 한다.
    # 즉, 어떤 DB가 생성되고 수정되고 삭제되는 일련의 과정들을 django에게 알려줘야 한다.
    
    ~/django-proj/webproj > python manage.py migrate
    
    ~/django-proj/webproj > python manage.py createsuperuser
    
    ```
    
- 계정 생성 후 접속