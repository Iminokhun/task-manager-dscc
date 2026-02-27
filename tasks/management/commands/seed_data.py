from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tasks.models import Comment, Project, Tag, Task


class Command(BaseCommand):
    help = "Seed database with demo users, projects, tags, tasks, and comments."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete Task/Comment data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Comment.objects.all().delete()
            Task.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing tasks/comments removed."))

        users = self._seed_users()
        projects = self._seed_projects(users)
        tags = self._seed_tags()
        tasks = self._seed_tasks(users, projects, tags)
        comments_count = self._seed_comments(users, tasks)

        self.stdout.write(self.style.SUCCESS("Seed completed successfully."))
        self.stdout.write(
            f"Users: {User.objects.count()}, "
            f"Projects: {Project.objects.count()}, "
            f"Tags: {Tag.objects.count()}, "
            f"Tasks: {Task.objects.count()}, "
            f"Comments: {Comment.objects.count()}"
        )
        self.stdout.write(f"Comments created/updated this run: {comments_count}")

    def _seed_users(self):
        users_data = [
            ("manager1", "manager1@example.com", True, False),
            ("manager2", "manager2@example.com", True, False),
            ("dev1", "dev1@example.com", False, False),
            ("dev2", "dev2@example.com", False, False),
            ("qa1", "qa1@example.com", False, False),
        ]

        users = {}
        for username, email, is_staff, is_superuser in users_data:
            user, _ = User.objects.get_or_create(username=username, defaults={"email": email})
            user.email = email
            user.is_active = True
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.set_password("Passw0rd!123")
            user.save()
            users[username] = user

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com"},
        )
        admin.email = "admin@example.com"
        admin.is_active = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("AdminPass!123")
        admin.save()
        users["admin"] = admin

        return users

    def _seed_projects(self, users):
        project_specs = [
            ("Website Revamp", "Refresh the public company website.", "manager1"),
            ("Mobile App", "Develop first MVP for Android and iOS.", "manager1"),
            ("Internal CRM", "Improve internal CRM workflows.", "manager2"),
            ("DevOps Migration", "Containerization and CI/CD rollout.", "manager2"),
        ]

        projects = {}
        for name, description, owner_username in project_specs:
            project, _ = Project.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "owner": users[owner_username],
                },
            )
            project.description = description
            project.owner = users[owner_username]
            project.save()
            projects[name] = project
        return projects

    def _seed_tags(self):
        tag_names = [
            "backend",
            "frontend",
            "bug",
            "urgent",
            "devops",
            "testing",
            "documentation",
        ]
        tags = {}
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag
        return tags

    def _seed_tasks(self, users, projects, tags):
        today = timezone.localdate()
        task_specs = [
            (
                "Design landing page hero",
                "Create and test new hero section visuals.",
                "in_progress",
                today + timedelta(days=3),
                "Website Revamp",
                "dev1",
                ["frontend", "urgent"],
            ),
            (
                "Fix login redirect bug",
                "Resolve incorrect redirect behavior after login.",
                "todo",
                today + timedelta(days=2),
                "Website Revamp",
                "dev2",
                ["backend", "bug"],
            ),
            (
                "Set up CI pipeline",
                "Add lint, tests, docker build, and deploy steps.",
                "in_progress",
                today + timedelta(days=5),
                "DevOps Migration",
                "dev1",
                ["devops", "backend"],
            ),
            (
                "Write API test scenarios",
                "Prepare regression scenarios for auth and tasks API.",
                "todo",
                None,
                "Internal CRM",
                "qa1",
                ["testing", "documentation"],
            ),
            (
                "Configure Redis cache",
                "Enable caching and session backend with Redis.",
                "done",
                today - timedelta(days=1),
                "DevOps Migration",
                "dev2",
                ["devops", "backend"],
            ),
            (
                "Refactor task detail template",
                "Improve readability and component structure.",
                "done",
                None,
                "Mobile App",
                "dev1",
                ["frontend"],
            ),
            (
                "Add project audit logs",
                "Track project-level updates in DB.",
                "todo",
                today + timedelta(days=7),
                "Internal CRM",
                None,
                ["backend"],
            ),
            (
                "Create deployment checklist",
                "Document pre-release checks for production.",
                "in_progress",
                today + timedelta(days=4),
                "DevOps Migration",
                "qa1",
                ["documentation", "devops"],
            ),
        ]

        tasks = {}
        for title, description, status, due_date, project_name, assignee_name, tag_names in task_specs:
            task, _ = Task.objects.get_or_create(
                title=title,
                defaults={
                    "description": description,
                    "status": status,
                    "due_date": due_date,
                    "project": projects[project_name],
                    "assignee": users.get(assignee_name) if assignee_name else None,
                },
            )
            task.description = description
            task.status = status
            task.due_date = due_date
            task.project = projects[project_name]
            task.assignee = users.get(assignee_name) if assignee_name else None
            task.save()
            task.tags.set([tags[name] for name in tag_names])
            tasks[title] = task
        return tasks

    def _seed_comments(self, users, tasks):
        comments_specs = [
            ("Design landing page hero", "manager1", "Please keep CTA above the fold."),
            ("Design landing page hero", "dev1", "Initial draft is done, needs review."),
            ("Fix login redirect bug", "qa1", "Reproducible on both Chrome and Firefox."),
            ("Set up CI pipeline", "manager2", "Make sure deployment runs only on main."),
            ("Set up CI pipeline", "dev1", "Lint and tests are already passing locally."),
            ("Write API test scenarios", "qa1", "I will add edge cases for invalid tokens."),
            ("Create deployment checklist", "manager2", "Add rollback steps before release."),
        ]

        created_or_updated = 0
        for task_title, author_username, body in comments_specs:
            comment, created = Comment.objects.get_or_create(
                task=tasks[task_title],
                author=users[author_username],
                body=body,
            )
            if not created:
                comment.body = body
                comment.save(update_fields=["body"])
            created_or_updated += 1
        return created_or_updated
