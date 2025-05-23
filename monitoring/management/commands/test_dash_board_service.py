from calendar import c

from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.domain.monitoring_project import MonitoringType
from monitoring.service.monitoring_project_service import MonitoringProjectService
from monitoring.service.monitoring_provision_service import MonitoringProvisionService
from user.domain.user import OAuthType, User


class Command(BaseCommand):
    help = "Test Grafana API capabilities"

    def handle(self, *args, **kwargs):
        monitoring_dashboard_service = MonitoringProvisionService()
        monitoring_project_service = MonitoringProjectService()
        # create_user_folder = monitoring_dashboard_service.create_user_folder(user_id="33333", user_name="33333333")
        # create_user_folder = monitoring_dashboard_service.create_service_account(user_id="33333")
        # create_user_folder = monitoring_dashboard_service.create_service_token(service_account_id=38, user_id="33333")
        # create_user_folder = monitoring_dashboard_service.set_folder_permissions(folder_uid="deml5in247x8ga", service_account_id=38)
        user = User(
            id="마지막",
            name="마지막",
            email="3473738fsdf@example.com",
            mobile_no="010-1324-5678",
            oauth_id="test_user999",
            oauth_type=OAuthType.KAKAO,
            tos_agreed=True,
            created_at=timezone.now().isoformat(),
            updated_at=timezone.now().isoformat(),
        )
        project = monitoring_project_service.create_project(
            user_id=user.id,
            name="test_project",
            project_type=MonitoringType.LOG,
            description="test_project_description",
        )
        provision_user_folder = monitoring_dashboard_service.provision_log_dashboard(
            user=user, monitoring_project_id=project.id, skip_base_provisioning=False
        )
