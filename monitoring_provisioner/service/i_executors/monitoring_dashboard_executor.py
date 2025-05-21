from abc import ABC, abstractmethod

from user.domain.user import User


class MonitoringDashboardTaskExecutor(ABC):

    @abstractmethod
    def dispatch_create_user_folder(
        self, task_id: str, user_id: str, folder_name: str
    ) -> str:
        """
        < 태스크 등록 >
        사용자 전용 폴더 생성
        """
        ...

    @abstractmethod
    def dispatch_create_service_account(
        self, task_id: str, account_name: str, user_id: str, role: str = "Viewer"
    ) -> str:
        """
        < 태스크 등록 >
        서비스 계정 생성
        """
        ...

    @abstractmethod
    def dispatch_create_service_token(
        self, task_id: str, service_account_id: int, token_name: str
    ) -> str:
        """
        < 태스크 등록 >
        서비스 계정 토큰 생성
        """
        ...

    @abstractmethod
    def dispatch_set_folder_permissions(
        self, task_id: str, folder_uid: str, service_account_id: int
    ) -> str:
        """
        < 태스크 등록 >
        폴더 권한 설정
        """
        ...

    @abstractmethod
    def dispatch_get_dashboard_by_uid(self, task_id: str, dashboard_uid: str) -> str:
        """
        < 태스크 등록 >
        대시보드 UID로 대시보드 조회
        """
        ...

    @abstractmethod
    def dispatch_get_grafana_folders(self, task_id: str) -> str:
        """
        < 태스크 등록 >
        대시보드 목록 조회
        """
        ...

    @abstractmethod
    def dispatch_create_public_dashboard(self, task_id: str, dashboard_uid: str) -> str:
        """
        < 태스크 등록 >
        공개용 대시보드 생성
        """
        ...

    @abstractmethod
    def dispatch_provision_user_folder(
        self,
        user: User,
        folder_task_id: str,
        account_task_id: str,
        token_task_id: str,
        perm_task_id: str,
        folder_name: str,
        account_name: str,
        token_name: str,
    ) -> str:
        """
        < 태스크 등록 >
        사용자 초기 폴더 관련 프로비저닝
        """
        ...
