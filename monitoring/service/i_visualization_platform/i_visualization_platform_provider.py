from abc import ABC, abstractmethod
from typing import Any


class VisualizationPlatformProvider(ABC):
    @abstractmethod
    def create_folder(self, title: str) -> dict[str, Any]:
        """Grafana에 폴더를 생성하고 결과 JSON을 반환."""
        pass

    @abstractmethod
    def create_service_account(self, name: str, role: str = "Viewer") -> dict[str, Any]:
        """서비스 계정 생성."""

        pass

    @abstractmethod
    def create_service_token(
        self, service_account_id: str, token_name: str
    ) -> dict[str, Any]:
        """서비스 계정 토큰 생성."""
        pass

    @abstractmethod
    def set_folder_permissions(
        self, folder_uid: str, service_account_id: str, permission: int = 1
    ) -> dict[str, Any]:
        """폴더 권한 설정."""
        pass

    @abstractmethod
    def create_dashboard(
        self, dashboard_data: dict[str, Any], folder_uid: str
    ) -> dict[str, Any]:
        """대시보드 생성."""
        pass

    @abstractmethod
    def create_public_dashboard(self, dashboard_uid: str) -> dict[str, Any]:
        """퍼블릭 대시보드 생성."""
        pass

    @abstractmethod
    def get_folders(self) -> list[dict[str, Any]]:
        """조회 가능한 폴더 목록 반환."""
        pass

    @abstractmethod
    def get_public_dashboard(self, public_dashboard_uid: str) -> dict[str, Any]:
        """퍼블릭 대시보드 정보 조회."""
        pass

    @abstractmethod
    def get_dashboard(self, uid: str) -> dict[str, Any]:
        """대시보드 정보 조회."""
        pass

    @abstractmethod
    def generate_dashboard_url(self, uid: str, token: str) -> str:
        """인증된 대시보드 URL 생성."""
        pass
