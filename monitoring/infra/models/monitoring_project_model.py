from django.db import models

from monitoring.domain.monitoring_project import MonitoringType, ProjectStatus
from monitoring.domain.visualization_platform import service_account
from monitoring.infra.models.visualization_platform_model import UserFolderModel
from user.infra.models.user import User


class MonitoringProjectModel(models.Model):
    id = models.CharField(primary_key=True, max_length=64)

    user = models.ForeignKey(
        User,
        to_field="id",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    project_type = models.CharField(
        max_length=32,
        choices=[(t.value, t.name) for t in MonitoringType],
    )

    status = models.CharField(
        max_length=32,
        choices=[(s.value, s.name) for s in ProjectStatus],
        default=ProjectStatus.INITIATED.value,
    )

    dashboard = models.OneToOneField(
        "DashboardModel",
        to_field="id",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        related_name="monitoring_project",
    )

    public_dashboard = models.OneToOneField(
        "PublicDashboardModel",
        to_field="id",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        related_name="monitoring_project",
    )

    service_account = models.OneToOneField(
        "ServiceAccountModel",
        to_field="id",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        related_name="monitoring_project",
    )

    user_folder = models.ForeignKey(
        UserFolderModel,
        to_field="id",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )

    agent_context = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "monitoring_project"
