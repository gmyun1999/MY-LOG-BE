from monitoring.domain.i_repo.i_monitoring_project_repo import IMonitoringProjectRepo
from monitoring.domain.monitoring_project import (
    AgentProvisioningContext,
    MonitoringProject,
    MonitoringType,
    ProjectStatus,
)
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
            )
        except MonitoringProjectModel.DoesNotExist:
            return None

    def update_status(self, project_id: str, status: str) -> None:
        MonitoringProjectModel.objects.filter(id=project_id).update(status=status)

    def update_fields(self, project_id: str, **fields: object) -> None:
        MonitoringProjectModel.objects.filter(id=project_id).update(**fields)
