"""One-time, idempotent setup. Run with `manage.py shell` after migrations.

ADMIN_EMAIL and ADMIN_PASSWORD must be passed as container environment variables.
Existing users/passwords and existing work items are never overwritten.
"""
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone
from plane.db.models import User, Profile, Workspace, WorkspaceMember, Project, ProjectMember, State, Cycle
from plane.license.models import Instance, InstanceAdmin, InstanceConfiguration


with transaction.atomic():
    instance = Instance.objects.first()
    if instance is None:
        instance = Instance.objects.create(
            instance_name="Sushi bar Sakura", instance_id=uuid.uuid4().hex,
            current_version="v1.4.2", last_checked_at=timezone.now(),
        )
    user, created = User.objects.get_or_create(
        email=os.environ["ADMIN_EMAIL"].lower(),
        defaults={"username": uuid.uuid4().hex, "first_name": "Shakhzod", "last_name": "Yokubov", "user_timezone": "Asia/Tashkent", "is_email_verified": True},
    )
    if created:
        user.set_password(os.environ["ADMIN_PASSWORD"])
        user.save()
    Profile.objects.get_or_create(user=user, defaults={"is_onboarded": True, "onboarding_step": {"profile_complete": True, "workspace_create": True, "workspace_invite": False, "workspace_join": True}})
    InstanceAdmin.objects.get_or_create(instance=instance, user=user)
    instance.is_setup_done = True
    instance.is_signup_screen_visited = True
    instance.is_telemetry_enabled = False
    instance.instance_name = "Sushi bar Sakura"
    instance.domain = "team.borili.uz"
    instance.save()
    for key, value in {"ENABLE_SIGNUP": "0", "ENABLE_MAGIC_LINK_LOGIN": "0", "ENABLE_EMAIL_PASSWORD": "1"}.items():
        InstanceConfiguration.objects.update_or_create(key=key, defaults={"value": value, "category": "AUTHENTICATION", "is_encrypted": False})
    workspace, _ = Workspace.objects.get_or_create(slug="sakura", defaults={"name": "Sushi bar Sakura", "owner": user, "timezone": "Asia/Tashkent"})
    WorkspaceMember.objects.get_or_create(workspace=workspace, member=user, defaults={"role": 20})
    project, _ = Project.objects.get_or_create(workspace=workspace, identifier="SAK", defaults={"name": "Sakura — Teamwork 2026", "project_lead": user, "network": 0, "cycle_view": True, "module_view": True, "timezone": "Asia/Tashkent"})
    ProjectMember.objects.get_or_create(project=project, workspace=workspace, member=user, defaults={"role": 20})
    for name, group, color in [("Backlog", "backlog", "#60646C"), ("To Do", "unstarted", "#60646C"), ("In Progress", "started", "#F59E0B"), ("Review", "started", "#8B5CF6"), ("Testing", "started", "#3B82F6"), ("Done", "completed", "#46A758")]:
        State.objects.get_or_create(project=project, name=name, defaults={"workspace": workspace, "group": group, "color": color, "default": name == "Backlog"})
    tz = ZoneInfo("Asia/Tashkent")
    for number, first, last in [(1, 2, 6), (2, 9, 13), (3, 16, 20), (4, 23, 27)]:
        Cycle.objects.get_or_create(project=project, name=f"Sprint {number}", defaults={"workspace": workspace, "owned_by": user, "start_date": datetime(2026, 11, first, 0, 0, tzinfo=tz), "end_date": datetime(2026, 11, last, 23, 59, tzinfo=tz), "timezone": "Asia/Tashkent"})
print("Sakura instance, admin, private workspace, board states and four sprints are ready.")
