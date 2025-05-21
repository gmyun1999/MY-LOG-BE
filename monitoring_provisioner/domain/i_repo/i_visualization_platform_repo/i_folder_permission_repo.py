from abc import ABC, abstractmethod

from monitoring_provisioner.domain.visualization_platform.folder import FolderPermission


class IFolderPermissionRepo(ABC):
    @abstractmethod
    def save(self, permission: FolderPermission) -> None:
        pass
