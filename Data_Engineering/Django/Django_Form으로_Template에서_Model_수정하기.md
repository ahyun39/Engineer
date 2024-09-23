> **form 만들기**

<br>

만들어뒀던 앱(homepage)에서 새로운 파일을 생성한다.

```python
# forms.py (homepage내에 생성)

from django import forms
from .models import Coffee # Model 호출

# 어떤 form을 만들지 작성해줘야 한다.
class CoffeeForm(forms.ModelForm): # ModelForm을 상속받는 Coffee Form 생성
	class Meta: # form을 만들기 위해서 어떤 모델을 써야하는지 class 안에 있는 class에서 지정이 된다.
		model = Coffee
		fields = {"name", "price", "is_ice"} # 어떤 field를 form에서 받을 것인지를 적어주는 곳이다.
```

- Model Form :  어떤 모델에 대해서 입력칸을 만들어주는 객체
- class Meta 내의 `Fields` : 위의 입력칸을 어떤 것으로 설정한 것인지에 대해
- class Meta 내의 `model` : 어떤 모델에 대한 Form을 만들 것인지에 대해

<br>

```python
# views.py
from .forms import CoffeeForm

def coffee_view(request):
    coffee_all = Coffee.objects.all()
    form = CoffeeForm()
    return render(request, 'coffee.html', {"coffee_list" : coffee_all, "coffee_form":form})
```

<br>
<br>

> **Template에서 Form 활용하기**


```html
# coffee.html
<!DOCTYPE html>
<html>
    <head>
        <title>Coffee List</title>
    </head>

    <body>
        <h1> My Coffee List </h1>
        {% for coffee in coffee_list %}
            <p>{{ coffee.name }} , {{ coffee.price }}</p>
        {% endfor %}
				
				# form을 활용하기 위해서는 <form></form> 을 추가해줘야 한다.
        <form>
						# as_p -> 정확한 form의 형태로 나타내기 위해서 사용한다.
						## coffee_form이 우리가 평소 봤던 그 형태로 랜더링이 된다.
            {{ coffee_form.as_p }}
        </form>
    </body>
</html>
```

<div style="display: flex;">
  <div style="flex: 1; padding-right: 10px;">
    <img width="230" alt="Untitled" src="https://github.com/user-attachments/assets/41526736-39c9-442b-9b03-7da503b0e811">
  </div>
  <div style="flex: 1; padding-left: 10px;">

    1. 왜 form의 순서가 바껴서 나올까.

    2. 저장하는 버튼은 생성되지 않았다.

  </div>
</div>

<br>

> **만들어진 form에 Button을 추가한다.**

<br>

```html
# coffee.html
<!DOCTYPE html>
<html>
    <head>
        <title>Coffee List</title>
    </head>

    <body>
        <h1> My Coffee List </h1>
        {% for coffee in coffee_list %}
            <p>{{ coffee.name }} , {{ coffee.price }}</p>
        {% endfor %}
				
				# form을 활용하기 위해서는 <form></form> 을 추가해줘야 한다.
        <form method="POST">
            {{ coffee_form.as_p }}
            <button type="submit">Save</button>
        </form>
    </body>
</html>
```

<img width="770" alt="Untitled (1)" src="https://github.com/user-attachments/assets/31101958-c436-4634-a706-8c7d3f380c36">

<br>
<br>

> **403 Error 해결하기**

<br>

```html
# coffee.html

<form method="POST">{% csrf_token %}
```

<br>
<br>

> **view에서 POST 요청을 보냈을 때 어떻게 하면 모델의 정보를 넣어줄 수 있을지**

<br>

```python
# views.py
def coffee_view(request):
    coffee_all = Coffee.objects.all()
    # 만약 request가 POST라면:
        # POST를 바탕으로 Form을 완성하고
        # Form이 유효하면 -> 저장
    if request.method == 'POST':
        form = CoffeeForm(request.POST) #POST를 보내줬던 내용을 바탕으로 Form을 완성시킨 것을 form이라고 한다.
		    if form.is_valid(): # form안에 들어있는 값이 유효한지 check
					form.save()
		form = CoffeeForm()
    return render(request, 'coffee.html', {"coffee_list" : coffee_all, "coffee_form":form})
```

<div style="display: flex;">
  <div style="flex: 1; padding-right: 10px;">
    <img width="276" alt="Untitled (4)" src="https://github.com/user-attachments/assets/ac7de1d8-38ae-4814-9b42-6206c262d5a7">
  </div>
  <div style="flex: 1; padding-left: 10px;">

    1. form에 입력된 결과가 출력까지 잘 되는 것을 확인할 수 있다.

  </div>
</div>



