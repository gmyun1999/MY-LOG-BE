from abc import ABC, abstractmethod
from typing import Any

from monitoring.service.i_executors.excutor_DTO import (
    BaseProvisionDTO,
    DashboardProvisionDTO,
)
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
    def dispatch_provision_base_resources_workflow(
        self,
        base_dto: BaseProvisionDTO,
    ) -> str:
        """
        < 태스크 등록 >
        사용자 초기 폴더 관련 프로비저닝
        """
        ...

    @abstractmethod
    def dispatch_provision_dashboard_workflow(
        self,
        dash_dto: DashboardProvisionDTO,
        base_dto: BaseProvisionDTO | None = None,
    ) -> str:
        """
        < 태스크 등록 >
        대시보드 프로비저닝
        1) 기본 리소스 프로비저닝
        2) 대시보드 템플릿 생성
        3) 퍼블릭 대시보드 생성
        """
        ...
