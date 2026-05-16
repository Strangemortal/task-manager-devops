import pytest
from django.contrib.auth import get_user_model

from main.forms import CommentForm, RegisterForm, TaskForm

User = get_user_model()


@pytest.mark.django_db
def test_register_form_valid():
    form_data = {
        "username": "newuser",
        "email": "new@example.com",
        "role": "backend",
        "password1": "pass123!",
        "password2": "pass123!",
    }
    form = RegisterForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_register_form_invalid():
    form_data = {
        "username": "newuser",
        "email": "invalid-email",
        "role": "backend",
    }
    form = RegisterForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_task_form_valid(regular_user):
    form_data = {
        "title": "New Task",
        "description": "Details",
        "assignees": [regular_user.id],
    }
    form = TaskForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_comment_form_valid():
    form_data = {"text": "Nice work!"}
    form = CommentForm(data=form_data)
    assert form.is_valid()
