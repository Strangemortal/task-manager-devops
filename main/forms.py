from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Task, Comment

class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('frontend', 'Frontend'), ('backend', 'Backend'), ('designer', 'Designer'), ('testing', 'Testing')])

    class Meta:
        model = User
        fields = ['username', 'email', 'role']
class TaskForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
