from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/menu/', views.get_dynamic_sidebar_menu, name='dynamic_menu'),
    path('dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    
    # App Store URL
    path('app-store/', views.app_store, name='app_store'),
    path('notification/read/<uuid:notification_id>/', views.read_notification, name='read_notification'),
]