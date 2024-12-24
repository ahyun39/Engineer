from django.urls import path
from . import views

urlpatterns = [
    path('', views.stamp_list, name='stamp_list'),
    path('create/', views.stamp_create, name='stamp_create'),
    path('update/<int:pk>/', views.stamp_update, name='stamp_update'),
    path('delete/<int:pk>/', views.stamp_delete, name='stamp_delete'),
]
