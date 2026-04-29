from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/create/', views.create_task, name='create_task'),
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('verify-task/<int:task_id>/', views.verify_task, name='verify_task'),
    path('reject-task/<int:task_id>/', views.reject_task, name='reject_task'),
    path('tasks/', views.task_list, name='task_list'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
]
