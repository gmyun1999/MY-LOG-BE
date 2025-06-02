from abc import ABC, abstractmethod

from monitoring.domain.visualization_platform.folder import FolderPermission


class IFolderPermissionRepo(ABC):
    @abstractmethod
    def save(self, permission: FolderPermission) -> None:
        pass

    @abstractmethod
    def find_by_service_account_id(
        self, service_account_id: str
    ) -> FolderPermission | None:
        pass
