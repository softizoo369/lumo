from django.urls import path
from . import views

urlpatterns = [
    # Client CRUD URLs
    path('clients/add/', views.client_create, name='client_create'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/<str:pk>/edit/', views.client_update, name='client_update'),
    path('clients/<str:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Invoice URLs (যা আমরা একটু আগে বানিয়েছি)
    path('invoices/new/', views.invoice_create, name='invoice_create'),
]