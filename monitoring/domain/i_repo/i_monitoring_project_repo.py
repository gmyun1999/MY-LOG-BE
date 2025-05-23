from abc import abstractmethod

from monitoring.domain.monitoring_project import MonitoringProject


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
