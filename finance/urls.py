from django.urls import path
from . import views

urlpatterns = [
    path('clients/add/', views.client_create, name='client_create'),
    path('clients/', views.client_list, name='client_list'),
]