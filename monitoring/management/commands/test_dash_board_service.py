from calendar import c

from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.service.monitoring_provision_service import MonitoringProvisionService
from user.domain.user import OAuthType, User


class Command(BaseCommand):
    help = "Test Grafana API capabilities"

    def handle(self, *args, **kwargs):
        monitoring_dashboard_service = MonitoringProvisionService()
        # create_user_folder = monitoring_dashboard_service.create_user_folder(user_id="33333", user_name="33333333")
        # create_user_folder = monitoring_dashboard_service.create_service_account(user_id="33333")
        # create_user_folder = monitoring_dashboard_service.create_service_token(service_account_id=38, user_id="33333")
        # create_user_folder = monitoring_dashboard_service.set_folder_permissions(folder_uid="deml5in247x8ga", service_account_id=38)
        user = User(
            id="test_user999",
            name="Test User999",
            email="test_user999@example.com",
            mobile_no="010-1324-5678",
            oauth_id="test_user999",
            oauth_type=OAuthType.KAKAO,
            tos_agreed=True,
            created_at=timezone.now().isoformat(),
            updated_at=timezone.now().isoformat(),
        )
        provision_user_folder = monitoring_dashboard_service.provision_dashboard(
            user=user
        )
