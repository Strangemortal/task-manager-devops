from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, RegisterForm, TaskForm
from .models import Comment, PersonalTodo, Task, TaskSubmission, User


# Helper: Superuser Check
def is_superuser(user):
    return user.is_superuser


@login_required
def update_task_status(request, task_id, new_status):
    valid_statuses = ["To Do", "In Progress", "Review", "Completed"]
    if new_status not in valid_statuses:
        return HttpResponseBadRequest("Invalid task status.")

    task = get_object_or_404(Task, id=task_id)

    # Only assigned members or admin can update status
    if request.user not in task.assignees.all() and not request.user.is_superuser:
        return HttpResponseForbidden("Permission denied.")

    task.status = new_status
    task.save()

    return redirect("task_detail", task_id=task.id)


# User Registration
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            return redirect("/login/?registered=1")
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})


# Login Logic
def user_login(request):
    info = None
    if request.GET.get("registered") == "1":
        info = (
            "Registration successful! Please wait for an admin to approve your "
            "account before logging in."
        )

    if request.method == "POST":
        uname = request.POST["username"]
        passwd = request.POST["password"]

        try:
            user_obj = User.objects.get(username=uname)
            if not user_obj.is_active and user_obj.check_password(passwd):
                return render(
                    request,
                    "main/login.html",
                    {"error": "Your account is pending admin approval.", "info": info},
                )
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=uname, password=passwd)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(
                request,
                "main/login.html",
                {"error": "Invalid credentials", "info": info},
            )
    return render(request, "main/login.html", {"info": info})


# User Logout
def user_logout(request):
    logout(request)
    return redirect("home")


# Home Page
def home(request):
    return render(request, "main/home.html")


# User Dashboard
@login_required
def dashboard(request):
    if request.user.is_superuser:
        tasks = Task.objects.prefetch_related("assignees").all()
    else:
        tasks = Task.objects.prefetch_related("assignees").filter(
            assignees=request.user
        )

    # Calculate stats
    stats = {
        "total": tasks.count(),
        "in_progress": tasks.filter(status="In Progress").count(),
    }

    return render(request, "main/dashboard.html", {"tasks": tasks, "stats": stats})


# Task Details and Comments
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Visibility Check: Only assigned members or admin
    if request.user not in task.assignees.all() and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to view this task.")

    comments = Comment.objects.filter(task=task).order_by("-timestamp")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect("task_detail", task_id=task.id)
    else:
        form = CommentForm()

    user_submission = TaskSubmission.objects.filter(task=task, user=request.user).first()
    submissions = TaskSubmission.objects.filter(task=task)
    submitted_users = [s.user for s in submissions]

    return render(
        request,
        "main/task_detail.html",
        {
            "task": task,
            "comments": comments,
            "form": form,
            "user_submission": user_submission,
            "submitted_users": submitted_users,
        },
    )


# Task Creation (only for superuser)
@user_passes_test(is_superuser)
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Many-to-many is handled by ModelForm.save()
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(request, "main/create_task.html", {"form": form})


@user_passes_test(is_superuser)
def superuser_dashboard(request):
    tasks_to_verify = Task.objects.filter(status="Completed")
    pending_users = User.objects.filter(is_active=False)
    return render(
        request,
        "main/superuser_dashboard.html",
        {"tasks": tasks_to_verify, "pending_users": pending_users},
    )


@user_passes_test(is_superuser)
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect("superuser_dashboard")


# Task Verification Logic
@user_passes_test(is_superuser)
def verify_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        is_verified = request.POST.get("verified") == "True"
        review_comment = request.POST.get("comment", "").strip()

        if is_verified:
            task.status = "Verified"
        else:
            task.status = "Rejected"
            TaskSubmission.objects.filter(task=task).delete()
            if review_comment:
                Comment.objects.create(
                    task=task, user=request.user, text=f"ADMIN REVIEW: {review_comment}"
                )
        task.save()
        return redirect("superuser_dashboard")

    return render(request, "main/verify_task.html", {"task": task})


@user_passes_test(is_superuser)
def reject_task(request, task_id):
    # This view can now just redirect to verify_task or we can keep it as a shortcut
    task = get_object_or_404(Task, id=task_id)
    task.status = "Rejected"
    TaskSubmission.objects.filter(task=task).delete()
    task.save()
    return redirect("superuser_dashboard")

@user_passes_test(is_superuser)
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect("dashboard")


@login_required
def task_list(request):
    if request.user.is_superuser:
        tasks = Task.objects.prefetch_related("assignees").all()
    else:
        tasks = Task.objects.prefetch_related("assignees").filter(
            assignees=request.user
        )

    status_filter = request.GET.get("status")
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    search_query = request.GET.get("search")
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    return render(request, "main/task_list.html", {"tasks": tasks})


@login_required
def toggle_todo(request, todo_id):
    todo = get_object_or_404(PersonalTodo, id=todo_id, user=request.user)
    todo.is_completed = not todo.is_completed
    todo.save()
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))


@login_required
def add_todo(request):
    if request.method == "POST":
        text = request.POST.get("todo_text", "").strip()
        if text:
            PersonalTodo.objects.create(user=request.user, text=text)
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))
@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Check if user is assigned to the task
    if request.user not in task.assignees.all():
        return HttpResponseForbidden("You are not assigned to this task.")

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if not message:
            return HttpResponseBadRequest("Submission message is required.")

        # Create or update submission
        TaskSubmission.objects.update_or_create(
            task=task, user=request.user, defaults={"message": message}
        )

        # Check if all assignees have submitted
        all_assignees = task.assignees.all()
        all_submissions = TaskSubmission.objects.filter(task=task)

        if all_submissions.count() >= all_assignees.count():
            # All members have submitted
            task.status = "Completed"
            task.save()

            # Merge all messages into a final comment
            final_message = "📢 FINAL SUBMISSION SUMMARY:\n"
            for sub in all_submissions:
                final_message += f"\n--- {sub.user.username}'s Report ---\n{sub.message}\n"

            Comment.objects.create(task=task, user=request.user, text=final_message)

        return redirect("task_detail", task_id=task.id)

    return redirect("task_detail", task_id=task.id)
