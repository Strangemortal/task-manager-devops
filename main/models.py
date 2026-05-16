from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ("frontend", "Frontend Developer"),
    ("backend", "Backend Developer"),
    ("designer", "UI/UX Designer"),
    ("testing", "Tester"),
    ("admin", "Admin"),
]


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="frontend")


class Task(models.Model):
    STATUS_CHOICES = [
        ("To Do", "To Do"),
        ("In Progress", "In Progress"),
        ("Review", "Review"),
        ("Completed", "Completed"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="To Do")
    assignees = models.ManyToManyField(User, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class VerificationRequest(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)


class PersonalTodo(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="personal_todos"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class TaskSubmission(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="submissions"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("task", "user")

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
