import uuid
from django.utils import timezone
from monitoring_provisioner.domain.task_result import TaskResult, TaskStatus
from monitoring_provisioner.infra.celery.tasks.grafana_tasks import (
    send_dashboard_creation_request,
    send_user_folder_creation_request
)
from monitoring_provisioner.infra.repository.task_result_repo import TaskResultRepository
from monitoring_provisioner.infra.repository.grafana_repo import GrafanaRepository
from monitoring_provisioner.service.i_executors.monitoring_dashboard_executor import MonitoringDashboardExecutor
from monitoring_provisioner.domain.grafana_dashboard import GrafanaDashboard


class GrafanaExecutor(MonitoringDashboardExecutor):
    
    def __init__(self):
        self.task_result_repo = TaskResultRepository()
        self.grafana_repo = GrafanaRepository()
    
    def create_user_folder(self, user_id: str, user_name: str) -> str:
        """
        사용자 전용 폴더 생성 요청을 Celery 태스크로 큐에 등록
        
        1. TaskResult 객체 생성 (PENDING 상태)
        2. DB에 저장 후 ID를 얻어옴
        3. send_user_folder_creation_request 태스크 호출
        4. 저장된 TaskResult ID 반환
        """
        # 고유 TaskResult ID와 Celery task_id 생성
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()

        # TaskResult 객체 구성
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="send_user_folder_creation_request",
            status=TaskStatus.PENDING,
            result={
                "user_id": user_id,
                "user_name": user_name
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        # DB에 저장
        saved_result = self.task_result_repo.save(task_result)
        
        # Celery 태스크 비동기 실행
        send_user_folder_creation_request.apply_async(
            args=(saved_result.id,),
            task_id=saved_result.task_id
        )
        
        # TaskResult ID 반환 (추후 상태 조회용)
        return saved_result.id
    
    def create_service_account(self, user_id: str) -> dict:
        """
        서비스 계정과 토큰을 즉시 생성 (동기 방식)
        
        1. Grafana API로 서비스 계정 생성
        2. 생성된 계정 ID로 토큰 발급
        3. 서비스 계정 ID와 토큰 키 반환
        """

        # Viewer 권한의 서비스 계정 생성
        service_account = self.grafana_repo.create_service_account(
            name=f"service-{user_id}",
            role="Viewer"
        )
        
        # 방금 생성한 계정에 사용할 API 토큰 생성
        token_result = self.grafana_repo.create_service_token(
            service_account_id=service_account["id"],
            token_name=f"token-{user_id}"
        )
        
        return {
            "service_account_id": service_account["id"],
            "service_token": token_result["key"]
        }
    
    def create_dashboard(self, user_id: str = None, title: str = None, panels: list = None) -> None:
        """
        대시보드 생성 요청 Celery 태스크로 큐에 등록
        
        1. TaskResult 객체 생성 (PENDING 상태)
        2. DB에 저장 후 ID를 얻어옴
        3. send_dashboard_creation_request 태스크 호출
        """

        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        # 기본 대시보드 정보 설정
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="send_dashboard_creation_request",
            status=TaskStatus.PENDING,
            result={
                "user_id": user_id,
                "title": title or f"Dashboard for User {user_id}",
                "panels": panels or [],
                # Folder UID와 서비스 토큰은 실제 구현에서는 DB에서 조회
                "folder_uid": None,
                "service_token": None
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        # Celery 태스크 비동기 실행
        send_dashboard_creation_request.apply_async(
            args=(saved_result.id,),
            task_id=saved_result.task_id
        )
    
    def get_dashboard(self, dashboard_uid: str) -> GrafanaDashboard:
        """
        Grafana API를 통해 UID 기반으로 대시보드 정보 조회
        """
        return self.grafana_repo.get_dashboard_by_uid(dashboard_uid)
    
    def get_user_dashboards(self, user_id: str) -> list:
        """
        Grafana API를 통해 특정 사용자가 소유한 대시보드 목록 조회
        """
        return self.grafana_repo.get_dashboards_by_user(user_id)