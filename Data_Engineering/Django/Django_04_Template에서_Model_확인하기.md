```python
# views.py
def coffee_view(request):

    return render(request, '', {})

# {}에 model에서 가져온 어떤 객체 즉 어떤 행들을 다 넣어주도록 할 것이다.

from .models import Coffee

def coffee_view(request):
	coffee_all = Coffee.objects.all() # .get(), .filter() ...
	return render(request, 'coffee.html', {"coffee_list" : coffee_all})
```

<br>

```html
# template > coffee.html

<!DOCTYPE html>
<html>
    <head>
        <title>Coffee List</title>
    </head>

    <body>
        <h1> My Coffee List </h1>
        <p>{{ coffee_list }}</p>
    </body>
</html>
```

<br>

```python
# urls.py

from homepage.views import coffee_view

path('coffee/',coffee_view)
```

<br>

**결과**

<img width="573" alt="Untitled (2)" src="https://github.com/user-attachments/assets/58a9b9d6-9e3c-405f-9b19-8cb3f39ae774">

<br>
<br>

---

### 위에서 QuerySet을 name , price로 나타낼 수 있게 다시 수정해본다.

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
    </body>
</html>
```

<br>

**결과**

<img width="574" alt="Untitled (3)" src="https://github.com/user-attachments/assets/88e18004-aa3d-44cd-b936-3d93e0a25222">