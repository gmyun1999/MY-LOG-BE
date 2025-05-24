from abc import abstractmethod

from monitoring.domain.monitoring_project import (
    MonitoringProject,
    MonitoringProjectWithBothDashboardsDto,
    MonitoringProjectWithDashboardDto,
    MonitoringProjectWithPublicDashboardDto,
)


class IMonitoringProjectRepo:
    @abstractmethod
    def save(self, project: MonitoringProject) -> None: ...

    @abstractmethod
    def find_by_id(self, project_id: str) -> MonitoringProject | None: ...

    @abstractmethod
    def update_status(self, project_id: str, status: str) -> None: ...

    @abstractmethod
    def update_fields(self, project_id: str, **fields: object) -> None: ...

    @abstractmethod
    def exists_by_id_and_user_id(self, project_id: str, user_id: str) -> bool: ...

    @abstractmethod
    def find_with_dashboard_dto(
        self, project_id: str
    ) -> MonitoringProjectWithDashboardDto | None: ...

    @abstractmethod
    def find_all_with_dashboard_dto_by_user(
        self, user_id: str
    ) -> list[MonitoringProjectWithDashboardDto]: ...

    @abstractmethod
    def find_with_public_dashboard_dto(
        self, project_id: str
    ) -> MonitoringProjectWithPublicDashboardDto | None: ...

    @abstractmethod
    def find_all_with_full_dashboard_dto_by_user(
        self, user_id: str
    ) -> list[MonitoringProjectWithBothDashboardsDto]: ...

    @abstractmethod
    def find_with_full_dashboard_dto(
        self, project_id: str
    ) -> MonitoringProjectWithBothDashboardsDto | None: ...
