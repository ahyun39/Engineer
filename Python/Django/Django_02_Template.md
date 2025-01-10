### render

<br>

render 함수

- 어떤 데이터를 바탕으로 ‘.html’ 안에 있는 내용을 완성한다는 느낌에 가깝다.

```python
# views.py
def index(request):
	return render(request, '.html', {})

# render 함수의 파라미터
## request : httprequest를 받은 것을 그대로 인자로 전달한 것.
## '.html': 응답을 하는 과정에서 보여줄 file을 지정
## {} : request, '.html'을 처리하는 과정에서 사용할 여러 인자들 (딕셔너리 형태로 전달)
```

<br>
<br>
<br>

### html 관리하는 방법 _ 여러 가지 ..

<br>

각 앱의 Directory에서 관리

- homepage > template (생성)
- template > index.html (생성)

<br>

**HTML**

- HTML은 열린 태그와 닫힌 태그로 이루어져있다.

```html
<!DOCTYPE html>
<html>

	<head>
		<title> </title>
	</head>

	<body>
		<h1> </h1>
		<p> </p>
	</body>

</html>
```

---

```html
<head>
# html file에 대한 메타적인 정보
# 보이는 부분이 아닌 그 뒤에서 이뤄지는 부분에 대한 작성
```

```html
<title> Python django example </title>
```

```html
</head>
```

---

```html
<body>
# 사용자가 눈으로 확인할 수 있는 요소
```

```html
<h1>Title</h1> # 제목과 같은 부분을 작성
<p>blah blah blah</p> # 문단 태그 (내용)
```

```html
</body>
```

<br>
<br>
<br>

### html 생성 이후

<br>

```python
# 생성한 html file을 render 함수의 두번째 인자로 작성해야한다.
render(request, 'index.html', {})
```

```python
webproj > settings.py

TEMPLATES = [
		'DIRS' : ['homepage/template/index.html'] # directory를 저장하는 곳
						 # Template들이 담긴 위치를 지정해줘야 한다.
]

# 'homepage/template/index.html' 라고 썼을 때의 문제
## django는 내 컴퓨터 상에서 WEBPROJ 디렉토리가 어디있는지 모른다.
## ['homepage/template/index.html'] -> [BASE_DIR + ...]

## 위 코드처럼 쓰기 보다는 os 사용해서 아래와 같이 작성한다.
 os.path.join(BASE_DIR,"homepage","template")
```

<img width="500" height="200" alt="Untitled (2)" src="https://github.com/user-attachments/assets/cdb80fe1-cdac-4092-9a5e-01b0b7786511">

<br>
<br>
<br>

### 실시간으로 변하는 정보들은 어떻게 처리할까

<br>

**고정되어 있는 변수에 대한**

```python
#views.py

def index(request):
	number = 10
	return render(request, 'index.html', {"my_num" : number})

#index.html

<body> 내에 작성
<p>{{ my_num }}</p> # my_num에 해당하는 정보를 출력하게 된다.
```

<br>

- **조건이나 반복의 로직 삽입 & template filter**
    
    <br>

    **template filter**
    
    - 변수의 값을 특정 형식으로 변환할 때 사용
    - 값의 길이 라던지 특정 값만 원할 때
    
    ```python
    # views.py
    
    def index(request):
    	name = "Michael"
    	return render(request, 'index.html', {"my_name" : name})
    
    # index.html
    <p>{{ my_name | length}}</p> # length(길이출력) 라는 filter 적용
    <p>{{ my_name | upper}}</p> # 모든 값이 대문자로
    ## document를 참고해서 원하는 filter를 찾아서 적용하면 된다.
    ```
    
    <br>

    **template tag**
    
    - for tag
        
        ```python
        #index.html
        <body> 내에 작성
        {% tag ... %} # 시작
        	적용할 로직을 작성
        {% endtag ... %} # 종료
        ## document를 참고해서 원하는 tag를 찾아서 적용하면 된다.
        
        # for tag
        {% for a in b %} # b는 template에 넘겨주는 데이터가 있어야 한다.
         ## views.py
            def index(request):
        				nums = [1,2,3,4,5]
        				return render(request, 'index.html', {"my_list" : nums})
         ## index.html
        		{% for element in my_list %}
        			<p>{{ element }}</p>
        		{% endfor %}
        ```
        
        <center><img  width="300" height="200" alt="Untitled (3)" src="https://github.com/user-attachments/assets/70198d02-b2a9-4fc7-9e4d-3b60b8403a45"></center>
        
    - if tag
        
        **if**
        
        ```python
        # if tag
        {% for element in my_list %}
        			# |(template filter)로 조건을 걸 수 있다.
        			# 짝수만 출력하게 하기
        			{% if element|divisibleby:"2" %} # element가 숫자 2으로 약분이 되면 element를 출력
        				<p>{{ element }}</p>
        			{% endif %}
        {% endfor %}
        ```
        
        <center><img  width="400" height="200"  alt="Untitled (4)" src="https://github.com/user-attachments/assets/874b33d7-ad35-4c1c-aa86-1ff04fc98d02"></center>
        
        **if not**
        
        ```python
        # if not tag
        {% for element in my_list %}
        			# |(template filter)로 조건을 걸 수 있다.
        			# 홀수만 출력하게 하기
        			{% if not element|divisibleby:"2" %}
        				<p>{{ element }}</p>
        			{% endif %}
        {% endfor %}
        ```
        
        <center><img  width="350" height="200" alt="Untitled (5)" src="https://github.com/user-attachments/assets/33771ba0-7289-41ac-920d-c66caab7d7f6"></center>