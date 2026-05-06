from .models import PersonalTodo

def personal_todos(request):
    if request.user.is_authenticated:
        return {
            'sidebar_todos': request.user.personal_todos.all().order_by('is_completed', '-created_at')
        }
    return {'sidebar_todos': []}
