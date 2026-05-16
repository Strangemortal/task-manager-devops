import pytest
from django.contrib.auth import get_user_model

from main.models import Task

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="test_admin",
        password="password123",
        email="admin@example.com",
        role="admin",
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="test_dev_user",
        password="password123",
        email="dev@example.com",
        role="frontend",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="test_other_user",
        password="password123",
        email="other@example.com",
        role="backend",
    )


@pytest.fixture
def sample_task(regular_user):
    task = Task.objects.create(
        title="Test Task", description="A test description", status="To Do"
    )
    task.assignees.add(regular_user)
    return task


@pytest.fixture
def authenticated_client(client, regular_user):
    client.login(username="test_dev_user", password="password123")
    return client


@pytest.fixture
def admin_client(client, admin_user):
    client.login(username="test_admin", password="password123")
    return client
