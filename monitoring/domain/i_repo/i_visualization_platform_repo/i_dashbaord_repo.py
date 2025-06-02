from abc import ABC, abstractmethod

from monitoring.domain.visualization_platform.dashboard import (
    Dashboard,
    PublicDashboard,
)


class IDashboardRepo(ABC):
    @abstractmethod
    def save(self, dashboard: Dashboard) -> None:
        """
        Dashboard 도메인 객체를 DB에 저장하거나 업데이트합니다.
        """
        ...

    @abstractmethod
    def find_by_uid(self, uid: str) -> Dashboard | None:
        """
        플랫폼 내부 UID로 Dashboard를 조회하여 도메인 객체로 반환합니다.
        """
        ...

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Dashboard | None:
        """
        사용자 ID로 Dashboard를 조회하여 도메인 객체로 반환합니다.
        """
        ...

    @abstractmethod
    def find_by_project_id(self, project_id: str) -> Dashboard | None: ...

    @abstractmethod
    def update_url(self, dashboard_id: str, url: str) -> None: ...


class IPublicDashboardRepo(ABC):
    @abstractmethod
    def save(self, public_dashboard: PublicDashboard) -> None:
        """
        퍼블릭 대시보드 도메인 객체를 DB에 저장하거나 업데이트합니다.
        """
        ...

    @abstractmethod
    def find_by_project_id(self, project_id: str) -> PublicDashboard | None:
        """
        프로젝트 ID로 퍼블릭 대시보드를 조회하여 도메인 객체로 반환합니다.
        """
        ...
