from dataclasses import fields

from monitoring.domain.i_repo.i_monitoring_project_repo import IMonitoringProjectRepo
from monitoring.domain.monitoring_project import (
    AgentProvisioningContext,
    MonitoringProject,
    MonitoringProjectWithDashboardDto,
    MonitoringType,
    ProjectStatus,
)
from monitoring.domain.visualization_platform.dashboard import Dashboard
from monitoring.infra.models.monitoring_project_model import MonitoringProjectModel


class MonitoringProjectRepo(IMonitoringProjectRepo):
    def save(self, project: MonitoringProject) -> None:
        MonitoringProjectModel.objects.update_or_create(
            id=project.id,
            defaults={
                "user_id": project.user_id,
                "name": project.name,
                "description": project.description,
                "project_type": project.project_type.value,
                "status": project.status.value,
                "dashboard_id": project.dashboard_id,
                "service_account_id": project.service_account_id,
                "user_folder_id": project.user_folder_id,
                "agent_context": (
                    project.agent_context.model_dump()
                    if project.agent_context
                    else None
                ),
            },
        )

    def find_by_id(self, project_id: str) -> MonitoringProject | None:
        try:
            obj = MonitoringProjectModel.objects.get(id=project_id)
            return MonitoringProject(
                id=obj.id,
                user_id=obj.user_id,
                name=obj.name,
                description=obj.description,
                project_type=MonitoringType(obj.project_type),
                status=ProjectStatus(obj.status),
                dashboard_id=obj.dashboard_id,
                user_folder_id=obj.user_folder_id,
                agent_context=(
                    AgentProvisioningContext(**obj.agent_context)
                    if obj.agent_context
                    else None
                ),
                service_account_id=obj.service_account_id,
            )
        except MonitoringProjectModel.DoesNotExist:
            return None

    def update_status(self, project_id: str, status: str) -> None:
        MonitoringProjectModel.objects.filter(id=project_id).update(status=status)

    def update_fields(self, project_id: str, **fields: object) -> None:
        MonitoringProjectModel.objects.filter(id=project_id).update(**fields)

    def exists_by_id_and_user_id(self, project_id: str, user_id: str) -> bool:
        return MonitoringProjectModel.objects.filter(
            id=project_id, user_id=user_id
        ).exists()

    def find_with_dashboard_dto(
        self, project_id: str
    ) -> MonitoringProjectWithDashboardDto | None:
        DASHBOARD_FIELD_KEYS = [
            Dashboard.FIELD_ID,
            Dashboard.FIELD_UID,
            Dashboard.FIELD_TITLE,
            Dashboard.FIELD_FOLDER_UID,
            Dashboard.FIELD_URL,
        ]

        # 1) 도메인 객체 조회
        project_domain = self.find_by_id(project_id)
        if project_domain is None:
            return None
        project_dict = project_domain.to_dict(
            excludes=[MonitoringProject.FIELD_AGENT_CONTEXT]
        )

        # 2) MonitoringProjectModel + dashboard 조회
        try:
            project_obj = MonitoringProjectModel.objects.select_related(
                "dashboard"
            ).get(id=project_id)
        except MonitoringProjectModel.DoesNotExist:
            return None

        # 3) dashboard_model이 None이면 그대로 None 할당
        dashboard_model = project_obj.dashboard
        if dashboard_model is None:
            dashboard_data = None
        else:
            dashboard_data = {
                key: getattr(dashboard_model, key) for key in DASHBOARD_FIELD_KEYS
            }

        # 4) DTO 생성
        combined = {
            **project_dict,
            "dashboard": dashboard_data,
        }
        return MonitoringProjectWithDashboardDto.from_dict(combined)

    def find_all_with_dashboard_dto_by_user(
        self, user_id: str
    ) -> list[MonitoringProjectWithDashboardDto]:
        # 1) 사용자 프로젝트 ID 목록 조회
        ids = MonitoringProjectModel.objects.filter(user_id=user_id).values_list(
            "id", flat=True
        )

        # 2) 각 ID별로 DTO 생성
        dtos: list[MonitoringProjectWithDashboardDto] = []
        for pid in ids:
            dto = self.find_with_dashboard_dto(pid)
            if dto is not None:
                dtos.append(dto)
        return dtos
