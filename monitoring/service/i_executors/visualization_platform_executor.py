from abc import ABC, abstractmethod

from monitoring.service.i_executors.excutor_DTO import (
    BaseProvisionDTO,
    DashboardProvisionDTO,
)


class VisualizationPlatformTaskExecutor(ABC):

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
