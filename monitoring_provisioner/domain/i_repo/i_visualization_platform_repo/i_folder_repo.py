from abc import ABC, abstractmethod
from typing import Optional

from monitoring_provisioner.domain.visualization_platform.folder import UserFolder


class IFolderRepo(ABC):
    @abstractmethod
    def save(self, folder: UserFolder) -> None:
        pass

    @abstractmethod
    def find_by_uid(self, uid: str) -> UserFolder | None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> UserFolder | None:
        pass
