from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stamps.urls')),  # stamps 앱 URL 연결
]
