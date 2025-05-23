from monitoring.domain.i_repo.i_visualization_platform_repo.i_dashbaord_repo import (
    IDashboardRepo,
)
from monitoring.domain.visualization_platform.dashboard import Dashboard
from monitoring.infra.models.visualization_platform_model import DashboardModel


class DashboardRepo(IDashboardRepo):
    def save(self, dashboard: Dashboard) -> None:
        """
        Dashboard 도메인 객체를 DB에 저장하거나 업데이트합니다.
        """
        DashboardModel.objects.update_or_create(
            id=dashboard.id, defaults=dashboard.to_dict()
        )

    def find_by_uid(self, uid: str) -> Dashboard | None:
        """
        플랫폼 내부 UID로 Dashboard를 조회하여 도메인 객체로 반환합니다.
        """
        try:
            model = DashboardModel.objects.get(uid=uid)
            return Dashboard(
                id=model.id,
                uid=model.uid,
                title=model.title,
                user_id=model.user_id,
                org_id=model.org_id,
                project_id=model.project_id,
                folder_uid=model.folder_uid,
                url=model.url,
                config_json=model.config_json,
                panels=model.panels,
                tags=model.tags,
                data_sources=model.data_sources,
            )
        except DashboardModel.DoesNotExist:
            return None

    def find_by_user_id(self, user_id: str) -> Dashboard | None:
        """
        사용자 ID로 Dashboard를 조회하여 도메인 객체로 반환합니다.
        """
        try:
            model = DashboardModel.objects.get(user_id=user_id)
            return Dashboard(
                id=model.id,
                uid=model.uid,
                title=model.title,
                user_id=model.user_id,
                org_id=model.org_id,
                project_id=model.project_id,
                folder_uid=model.folder_uid,
                url=model.url,
                config_json=model.config_json,
                panels=model.panels,
                tags=model.tags,
                data_sources=model.data_sources,
            )
        except DashboardModel.DoesNotExist:
            return None

    def find_by_project_id(self, project_id: str) -> Dashboard | None:
        """
        프로젝트 ID로 Dashboard를 조회하여 도메인 객체로 반환합니다.
        """
        try:
            model = DashboardModel.objects.get(project_id=project_id)
            return Dashboard(
                id=model.id,
                uid=model.uid,
                title=model.title,
                user_id=model.user_id,
                org_id=model.org_id,
                project_id=model.project_id,
                folder_uid=model.folder_uid,
                url=model.url,
                config_json=model.config_json,
                panels=model.panels,
                tags=model.tags,
                data_sources=model.data_sources,
            )
        except DashboardModel.DoesNotExist:
            return None
