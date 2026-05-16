from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Task, User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ("frontend", "Frontend"),
            ("backend", "Backend"),
            ("designer", "Designer"),
            ("testing", "Testing"),
        ]
    )

    class Meta:
        model = User
        fields = ["username", "email", "role"]


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple, required=True
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assignees"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
