from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, TaskForm
from .models import Project, Task


def home(request):
    return redirect("task_list")


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def task_list(request):
    tasks = Task.objects.select_related("project", "assignee").prefetch_related("tags").all()
    return render(request, "tasks/task_list.html", {"tasks": tasks})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form, "title": "Create Task"})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "title": "Edit Task"})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
def project_list(request):
    projects = Project.objects.select_related("owner").all()
    return render(request, "tasks/project_list.html", {"projects": projects})
