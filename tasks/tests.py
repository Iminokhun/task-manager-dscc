import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from uuid import uuid4

from tasks.models import Comment, Project, Tag, Task


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="StrongPass123!")


@pytest.fixture
def project(user):
    return Project.objects.create(
        name="Test Project",
        description="Project for tests",
        owner=user,
    )


@pytest.mark.django_db
def test_register_page_loads(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_login(client):
    User.objects.create_user(username="alice", password="StrongPass123!")
    response = client.post(
        reverse("login"),
        {"username": "alice", "password": "StrongPass123!"},
    )
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_task_list_requires_auth(client):
    response = client.get(reverse("task_list"))
    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_create_task_authenticated(client, user, project):
    client.login(username="testuser", password="StrongPass123!")
    response = client.post(
        reverse("task_create"),
        {
            "title": "Created by test",
            "description": "Task description",
            "status": "todo",
            "project": project.id,
            "assignee": user.id,
            "tags": [],
        },
    )
    assert response.status_code == 302
    assert Task.objects.filter(title="Created by test", project=project).exists()


@pytest.mark.django_db
def test_update_task(client, user, project):
    task = Task.objects.create(
        title="Old title",
        description="Old desc",
        status="todo",
        project=project,
        assignee=user,
    )
    client.login(username="testuser", password="StrongPass123!")
    response = client.post(
        reverse("task_update", kwargs={"pk": task.pk}),
        {
            "title": "Updated title",
            "description": "Updated desc",
            "status": "in_progress",
            "project": project.id,
            "assignee": user.id,
            "tags": [],
        },
    )
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.title == "Updated title"
    assert task.status == "in_progress"


@pytest.mark.django_db
def test_add_comment_to_task_detail(client, user, project):
    task = Task.objects.create(
        title="Task with comments",
        description="Task description",
        status="todo",
        project=project,
    )
    client.login(username="testuser", password="StrongPass123!")
    response = client.post(
        reverse("task_detail", kwargs={"pk": task.pk}),
        {"body": "New comment from test"},
    )
    assert response.status_code == 302
    assert Comment.objects.filter(
        task=task, author=user, body="New comment from test"
    ).exists()


@pytest.mark.django_db
def test_task_tag_many_to_many_relation(user, project):
    task = Task.objects.create(
        title="Task with tags",
        description="Task description",
        status="todo",
        project=project,
    )
    tag_backend = Tag.objects.create(name=f"backend-{uuid4().hex[:8]}")
    tag_bug = Tag.objects.create(name=f"bug-{uuid4().hex[:8]}")

    task.tags.add(tag_backend, tag_bug)

    assert task.tags.count() == 2
    assert set(task.tags.values_list("name", flat=True)) == {
        tag_backend.name,
        tag_bug.name,
    }
