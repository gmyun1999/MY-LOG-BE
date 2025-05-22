from django.db import models

from monitoring.domain.visualization_platform.folder import FolderPermissionLevel
from user.infra.models.user import User


class ServiceAccountModel(models.Model):
    """
    시각화 플랫폼의 서비스 계정
    """

    id = models.CharField(primary_key=True, max_length=64)
    account_id = models.IntegerField(unique=True)

    user = models.ForeignKey(
        User, to_field="id", on_delete=models.DO_NOTHING, db_constraint=False
    )

    name = models.CharField(max_length=128)
    is_disabled = models.BooleanField(default=False)
    role = models.CharField(max_length=32)
    token = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "visualization_service_account"


class DashboardModel(models.Model):
    """
    시각화 플랫폼 대시보드
    """

    id = models.CharField(primary_key=True, max_length=64)
    uid = models.CharField(max_length=128, null=True, blank=True)

    title = models.CharField(max_length=256, null=True, blank=True)

    user = models.ForeignKey(
        User,
        to_field="id",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )

    org_id = models.CharField(max_length=64, null=True, blank=True)
    folder_uid = models.CharField(max_length=128, null=True, blank=True)
    url = models.URLField(max_length=512, null=True, blank=True)

    config_json = models.JSONField(null=True, blank=True)
    panels = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    data_sources = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "visualization_dashboard"


class FolderPermissionModel(models.Model):
    """
    서비스 계정 ↔ 폴더 권한
    """

    id = models.CharField(primary_key=True, max_length=64)

    service_account = models.ForeignKey(
        ServiceAccountModel,
        to_field="account_id",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )

    folder_uid = models.CharField(max_length=128)

    permission = models.IntegerField(
        choices=[
            (level.value, level.name.capitalize()) for level in FolderPermissionLevel
        ]
    )

    class Meta:
        db_table = "visualization_folder_permission"
        unique_together = ("service_account", "folder_uid")


class UserFolderModel(models.Model):
    id = models.CharField(primary_key=True, max_length=64)

    user = models.ForeignKey(
        User,
        to_field="id",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        null=True,
        blank=True,
    )

    uid = models.CharField(max_length=128, unique=True)  # folder UID
    name = models.CharField(max_length=255)
    org_id = models.CharField(max_length=64, null=True, blank=True)
    created_by_task = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = "visualization_folder"
