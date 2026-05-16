import pytest
from django.urls import reverse

from main.models import PersonalTodo, Task, User


@pytest.mark.django_db
def test_home_view_redirects_if_not_logged_in(client):
    response = client.get(reverse("home"))
    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_dashboard_view_authenticated(authenticated_client):
    response = authenticated_client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert "tasks" in response.context


@pytest.mark.django_db
def test_task_detail_view_permission(authenticated_client, other_user):
    # Create a task assigned to someone else
    other_task = Task.objects.create(title="Other Task", description="Desc")
    other_task.assignees.add(other_user)
    url = reverse("task_detail", args=[other_task.id])
    response = authenticated_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_task_status(authenticated_client, sample_task):
    url = reverse("update_task_status", args=[sample_task.id, "In Progress"])
    response = authenticated_client.get(url)
    assert response.status_code == 302
    sample_task.refresh_from_db()
    assert sample_task.status == "In Progress"


@pytest.mark.django_db
def test_registration_flow(client):
    url = reverse("register")
    data = {
        "username": "new_dev",
        "email": "new_dev@example.com",
        "role": "designer",
        "password1": "securepass123",
        "password2": "securepass123",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    new_user = User.objects.get(username="new_dev")
    assert new_user.is_active is False  # Needs admin approval


@pytest.mark.django_db
def test_admin_approval_view(admin_client, regular_user):
    regular_user.is_active = False
    regular_user.save()
    url = reverse("approve_user", args=[regular_user.id])
    response = admin_client.get(url)
    assert response.status_code == 302
    regular_user.refresh_from_db()
    assert regular_user.is_active is True


@pytest.mark.django_db
def test_task_verification_approve(admin_client, sample_task):
    sample_task.status = "Completed"
    sample_task.save()
    url = reverse("verify_task", args=[sample_task.id])
    response = admin_client.post(url, {"verified": "True"})
    assert response.status_code == 302
    sample_task.refresh_from_db()
    assert sample_task.status == "Verified"


@pytest.mark.django_db
def test_task_verification_reject(admin_client, sample_task):
    sample_task.status = "Completed"
    sample_task.save()
    url = reverse("verify_task", args=[sample_task.id])
    response = admin_client.post(
        url, {"verified": "False", "comment": "Fix documentation"}
    )
    assert response.status_code == 302
    sample_task.refresh_from_db()
    assert sample_task.status == "Rejected"
    assert sample_task.comment_set.filter(text__icontains="Fix documentation").exists()


@pytest.mark.django_db
def test_toggle_todo(authenticated_client, sample_task, regular_user):
    todo = PersonalTodo.objects.get(user=regular_user, task=sample_task)
    url = reverse("toggle_todo", args=[todo.id])
    response = authenticated_client.get(url)
    assert response.status_code == 302
    todo.refresh_from_db()
    assert todo.is_completed is True


@pytest.mark.django_db
def test_task_list_search(authenticated_client, sample_task):
    url = reverse("task_list") + "?search=Test"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert sample_task in response.context["tasks"]

    url = reverse("task_list") + "?search=Nonexistent"
    response = authenticated_client.get(url)
    assert sample_task not in response.context["tasks"]


@pytest.mark.django_db
def test_add_todo(authenticated_client, regular_user):
    url = reverse("add_todo")
    response = authenticated_client.post(url, {"todo_text": "My New Custom Todo"})
    assert response.status_code == 302
    assert PersonalTodo.objects.filter(
        user=regular_user, text="My New Custom Todo"
    ).exists()
