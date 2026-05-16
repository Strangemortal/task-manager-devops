import pytest

from main.models import Comment, PersonalTodo


@pytest.mark.django_db
def test_user_creation(regular_user):
    assert regular_user.username == "test_dev_user"
    assert regular_user.role == "frontend"
    assert str(regular_user) == "test_dev_user"


@pytest.mark.django_db
def test_task_creation(sample_task, regular_user):
    assert sample_task.title == "Test Task"
    assert regular_user in sample_task.assignees.all()
    assert sample_task.status == "To Do"
    assert str(sample_task) == "Test Task"


@pytest.mark.django_db
def test_personal_todo_signal(sample_task, regular_user):
    # The signal should create a PersonalTodo automatically
    todo = PersonalTodo.objects.filter(user=regular_user, task=sample_task).first()
    assert todo is not None
    assert todo.text == f"Task: {sample_task.title}"
    assert todo.is_completed is False
    assert str(todo) == f"Task: {sample_task.title}"


@pytest.mark.django_db
def test_comment_creation(sample_task, regular_user):
    comment = Comment.objects.create(
        task=sample_task, user=regular_user, text="A test comment"
    )
    assert comment.task == sample_task
    assert comment.user == regular_user
    assert comment.text == "A test comment"
