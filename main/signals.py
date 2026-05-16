from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import PersonalTodo, Task


@receiver(m2m_changed, sender=Task.assignees.through)
def sync_personal_todos(sender, instance, action, pk_set, **kwargs):
    """
    Ensures that every assigned member has a PersonalTodo for this task.
    Handles adding and removing members.
    """
    if action == "post_add":
        for user_id in pk_set:
            PersonalTodo.objects.get_or_create(
                user_id=user_id,
                task=instance,
                defaults={"text": f"Task: {instance.title}", "is_completed": False},
            )
    elif action == "post_remove":
        for user_id in pk_set:
            PersonalTodo.objects.filter(user_id=user_id, task=instance).delete()


@receiver(post_save, sender=Task)
def update_todo_text(sender, instance, **kwargs):
    """
    Updates the text of existing PersonalTodos if the Task title changes.
    """
    PersonalTodo.objects.filter(task=instance).update(text=f"Task: {instance.title}")
