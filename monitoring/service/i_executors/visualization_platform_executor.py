from abc import ABC, abstractmethod

from monitoring.service.i_executors.excutor_DTO import (
    CreateDashboardDTO,
    CreatePublicDashboardDTO,
    CreateServiceAccountDTO,
    CreateServiceTokenDTO,
    CreateUserFolderDTO,
    FinalizeDashboardDTO,
    ProvisionFailureDTO,
    SetFolderPermissionsDTO,
)


class VisualizationPlatformTaskExecutor(ABC):

    @abstractmethod
    def dispatch_provision_dashboard_workflow(
        self,
        *,
        user_folder: CreateUserFolderDTO | None = None,
        service_account: CreateServiceAccountDTO | None = None,
        service_token: CreateServiceTokenDTO | None = None,
        permissions: SetFolderPermissionsDTO | None = None,
        dashboard: CreateDashboardDTO | None = None,
        public_dashboard: CreatePublicDashboardDTO | None = None,
        finalize_dashboard: FinalizeDashboardDTO | None = None,
        failure: ProvisionFailureDTO,
    ) -> str:
        """
        < 태스크 등록 >
        대시보드 프로비저닝
        1) 기본 리소스 프로비저닝
        2) 대시보드 템플릿 생성
        3) 퍼블릭 대시보드 생성
        """
        ...
