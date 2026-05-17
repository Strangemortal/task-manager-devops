from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r"^$", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("task/<int:task_id>/", views.task_detail, name="task_detail"),
    path("task/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("task/create/", views.create_task, name="create_task"),
    path("superuser-dashboard/", views.superuser_dashboard, name="superuser_dashboard"),
    path("verify-task/<int:task_id>/", views.verify_task, name="verify_task"),
    path("reject-task/<int:task_id>/", views.reject_task, name="reject_task"),
    path("tasks/", views.task_list, name="task_list"),
    path("approve-user/<int:user_id>/", views.approve_user, name="approve_user"),
    path(
        "task/<int:task_id>/update-status/<str:new_status>/",
        views.update_task_status,
        name="update_task_status",
    ),
    path("todo/toggle/<int:todo_id>/", views.toggle_todo, name="toggle_todo"),
    path("todo/add/", views.add_todo, name="add_todo"),
    path("task/<int:task_id>/submit/", views.submit_task, name="submit_task"),
]
