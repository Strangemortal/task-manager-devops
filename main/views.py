from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Task, Comment, VerificationRequest, User
from .forms import RegisterForm, TaskForm, CommentForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from .models import Task
def assign_role_to_user(user, group_name):
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()
@login_required
def update_task_status(request, task_id, new_status):
    # Define allowed status transitions
    valid_statuses = ['To Do', 'In Progress', 'Review', 'Completed']
    
    if new_status not in valid_statuses:
        return HttpResponseBadRequest("Invalid task status.")  # More appropriate than HttpResponse
    
    task: Task = get_object_or_404(Task, id=task_id)

    # Optional: enforce rules like only assignee or superuser can update status
    if request.user != task.assignee and not request.user.is_superuser:
        return HttpResponseBadRequest("Permission denied.")
    
    task.status = new_status
    task.save()
    
    return redirect('task_detail', task_id=task.id)


def assign_roles(request):
    # Create groups (roles)
    admin_group, created = Group.objects.get_or_create(name='Admin')
    manager_group, created = Group.objects.get_or_create(name='Manager')
    user_group, created = Group.objects.get_or_create(name='User')

    # Assign permissions to Admin (Full access)
    admin_permissions = Permission.objects.all()
    admin_group.permissions.set(admin_permissions)

    # Assign permissions to Manager (Manage Tasks)
    task_content_type = ContentType.objects.get_for_model(Task)
    manager_permissions = Permission.objects.filter(content_type=task_content_type)
    manager_group.permissions.set(manager_permissions)

    # Assign basic permissions to User (View and Create Tasks)
    user_permissions = Permission.objects.filter(codename__in=['add_task', 'view_task'])
    user_group.permissions.set(user_permissions)

    return HttpResponse("Roles and permissions assigned.")
# User Registration
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            return redirect('/login/?registered=1')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

# Login Logic
def user_login(request):
    info = None
    if request.GET.get('registered') == '1':
        info = "Registration successful! Please wait for an admin to approve your account before logging in."

    if request.method == 'POST':
        uname = request.POST['username']
        passwd = request.POST['password']
        
        try:
            user_obj = User.objects.get(username=uname)
            if not user_obj.is_active and user_obj.check_password(passwd):
                return render(request, 'main/login.html', {'error': 'Your account is pending admin approval.', 'info': info})
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=uname, password=passwd)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'main/login.html', {'error': 'Invalid credentials', 'info': info})
    return render(request, 'main/login.html', {'info': info})

# User Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Home Page
@login_required(login_url='/login/')
def home(request):
    return render(request, 'main/home.html')

# User Dashboard
@login_required
def dashboard(request):
    if request.user.role == 'admin':
        tasks = Task.objects.all()
    else:
        tasks = request.user.task_set.all()
    return render(request, 'main/dashboard.html', {'tasks': tasks})

# Task Details and Comments
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = Comment.objects.filter(task=task)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
    else:
        form = CommentForm()
    return render(request, 'main/task_detail.html', {'task': task, 'comments': comments, 'form': form})

# Task Creation (only for superuser)
@login_required

def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assignee = User.objects.get(id=request.POST.get('assignee'))
            task.save()
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'main/create_task.html', {'form': form})

# Superuser Check
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def superuser_dashboard(request):
    tasks_to_verify = Task.objects.filter(status='Completed')
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'main/superuser_dashboard.html', {'tasks': tasks_to_verify, 'pending_users': pending_users})

@user_passes_test(is_superuser)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('superuser_dashboard')


# Task Verification Logic
@user_passes_test(lambda u: u.is_superuser)
def verify_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        # Update task status based on verification
        is_verified = request.POST.get('verified') == 'True'
        if is_verified:
            task.status = 'Verified'
        else:
            task.status = 'Rejected'
        task.save()
        return redirect('superuser_dashboard')  # Redirect after verification

    return render(request, 'main/verify_task.html', {'task': task})

# Reject Task Logic
@user_passes_test(is_superuser)
def reject_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.status = 'Rejected'
    task.save()
    return redirect('superuser_dashboard')

def task_list(request):
    tasks = Task.objects.all()

    # Filter by status if provided in GET parameters
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Search by title if provided
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    return render(request, 'main/task_list.html', {'tasks': tasks})

