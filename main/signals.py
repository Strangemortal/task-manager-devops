from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, PersonalTodo

@receiver(post_save, sender=Task)
def create_personal_todo(sender, instance, created, **kwargs):
    if created:
        PersonalTodo.objects.get_or_create(
            user=instance.assignee,
            task=instance,
            text=f"Task: {instance.title}",
            defaults={'is_completed': False}
        )
