from abc import ABC, abstractmethod

from monitoring_provisioner.domain.visualization_platform.service_account import (
    ServiceAccount,
)


class IServiceAccountRepo(ABC):
    @abstractmethod
    def save(self, account: ServiceAccount) -> None:
        pass

    @abstractmethod
    def find_by_account_id(self, account_id: int) -> ServiceAccount | None:
        pass

    @abstractmethod
    def update_token(self, account_id: int, token: str) -> None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> ServiceAccount | None:
        pass
