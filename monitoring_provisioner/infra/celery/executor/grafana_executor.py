import uuid
from typing import Optional, Dict, Any
from django.utils import timezone
from monitoring_provisioner.domain.task_result import TaskResult, TaskStatus
from monitoring_provisioner.infra.celery.tasks.grafana_tasks import (
    create_grafana_folder,
    create_grafana_service_account,
    create_grafana_service_token,
    set_grafana_folder_permissions,
    create_grafana_dashboard,
    get_grafana_dashboard,
    get_grafana_folders,
    create_grafana_public_dashboard,
    create_grafana_logs_dashboard
    
)
from monitoring_provisioner.infra.repository.task_result_repo import TaskResultRepository
from monitoring_provisioner.service.i_executors.monitoring_dashboard_executor import MonitoringDashboardExecutor


class GrafanaExecutor(MonitoringDashboardExecutor):
    
    def __init__(self):
        self.task_result_repo = TaskResultRepository()
    
    def create_user_folder(self, user_id: str, user_name: str) -> str:
        """
        사용자 폴더 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        folder_name = f"User_{user_id}_{user_name}'s Folder"
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_folder",
            status=TaskStatus.PENDING,
            result={
                "folder_name": folder_name,
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
        create_grafana_folder.apply_async(
            args=(saved_result.id, folder_name),  # task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def create_service_account(self, user_id: str, role: str = "Viewer") -> str:
        """
        서비스 계정 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        account_name = f"service-{user_id}"
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_service_account",
            status=TaskStatus.PENDING,
            result={
                "name": account_name,
                "role": role,
                "user_id": user_id
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        create_grafana_service_account.apply_async(
            args=(saved_result.id, account_name, role),  # task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def create_service_token(self, service_account_id: int, user_id: str) -> str:
        """
        서비스 토큰 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        token_name = f"token-{user_id}"
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_service_token",
            status=TaskStatus.PENDING,
            result={
                "service_account_id": service_account_id,
                "token_name": token_name,
                "user_id": user_id
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        create_grafana_service_token.apply_async(
            args=(saved_result.id, service_account_id, token_name),  # task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def set_folder_permissions(self, folder_uid: str, service_account_id: int) -> str:
        """
        폴더 권한 설정 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="set_grafana_folder_permissions",
            status=TaskStatus.PENDING,
            result={
                "folder_uid": folder_uid,
                "service_account_id": service_account_id
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        set_grafana_folder_permissions.apply_async(
            args=(saved_result.id, folder_uid, service_account_id),  # 수정: task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def create_dashboard(self, user_id: str = None, title: str = None, panels: list = None, folder_uid: str = None) -> str:
        """
        대시보드 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        # folder_uid가 제공되지 않은 경우
        # 태스크 결과 DB에서 검색
        if folder_uid is None and user_id:
            try:
                from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
                # 해당 사용자의 가장 최근 폴더 생성 태스크 조회
                recent_folder_task = TaskResultModel.objects.filter(
                    task_name="create_grafana_folder",
                    result__contains=user_id,  # JSON 필드 검색
                    status=TaskStatus.SUCCESS
                ).order_by('-date_done').first()
                
                if recent_folder_task and recent_folder_task.result:
                    # 성공한 응답에서 폴더 UID 추출
                    result_data = recent_folder_task.result
                    if isinstance(result_data, dict) and 'uid' in result_data:
                        folder_uid = result_data['uid']
                        print(f"사용자 {user_id}의 최근 폴더 UID: {folder_uid}")
            except Exception as e:
                print(f"폴더 UID 검색 실패: {str(e)}")
        
        # Grafana API 직접 호출
        if folder_uid is None and user_id:
            try:
                from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
                api = GrafanaAPI()
                folders = api.get_folders()
                
                # 폴더 이름 패턴
                folder_pattern = f"User_{user_id}_"
                
                for folder in folders:
                    if folder_pattern in folder.get('title', ''):
                        folder_uid = folder.get('uid')
                        print(f"그라파나 API에서 찾은 폴더 UID: {folder_uid}")
                        break
            except Exception as e:
                print(f"그라파나 API에서 폴더 UID 검색 실패: {str(e)}")
        
        dashboard_data = {
            "title": title or f"Dashboard for User {user_id}",
            "uid": f"user-{user_id}-{uuid.uuid4().hex[:8]}",
            "tags": ["auto-generated", f"user-{user_id}"],
            "panels": panels or [
                {
                    "id": 1,
                    "type": "graph",
                    "title": "샘플 그래프",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                }
            ]
        }
        
        # 태스크 결과 생성 및 저장
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_dashboard",
            status=TaskStatus.PENDING,
            result={
                "dashboard_data": dashboard_data,
                "folder_uid": folder_uid,  # 이 값이 None이 아니어야 함
                "user_id": user_id
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        create_grafana_dashboard.apply_async(
            args=(saved_result.id, dashboard_data, folder_uid),
            task_id=saved_result.task_id
        )
        
        print(f"대시보드 생성 요청: dashboard_data={dashboard_data}, folder_uid={folder_uid}")
        return saved_result.id
    
    def get_dashboard(self, dashboard_uid: str) -> str:
        """
        대시보드 조회 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="get_grafana_dashboard",
            status=TaskStatus.PENDING,
            result={
                "dashboard_uid": dashboard_uid
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        get_grafana_dashboard.apply_async(
            args=(saved_result.id, dashboard_uid),  # task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def get_user_dashboards(self, user_id: str) -> str:
        """
        사용자 대시보드 목록 조회
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="get_grafana_folders",
            status=TaskStatus.PENDING,
            result={
                "user_id": user_id
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        get_grafana_folders.apply_async(
            args=(saved_result.id,),  # task_result_id를 첫 번째 인자로 전달
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def create_public_dashboard(self, dashboard_uid: str) -> str:
        """
        퍼블릭 대시보드 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_public_dashboard",
            status=TaskStatus.PENDING,
            result={
                "dashboard_uid": dashboard_uid
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        create_grafana_public_dashboard.apply_async(
            args=(saved_result.id, dashboard_uid),
            task_id=saved_result.task_id
        )
        
        return saved_result.id
    
    def create_logs_dashboard(self, user_id: str, user_name: str, folder_uid: str = None, 
                         data_source_uid: str = "Elasticsearch") -> str:
        """
        로그 대시보드 생성 태스크 요청
        """
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()
        
        # folder_uid가 제공되지 않은 경우 검색
        if folder_uid is None:
            folder_uid = self._find_folder_uid_for_user(user_id)
        
        # 태스크 결과 생성 및 저장
        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="create_grafana_logs_dashboard",
            status=TaskStatus.PENDING,
            result={
                "user_id": user_id,
                "user_name": user_name,
                "folder_uid": folder_uid,
                "data_source_uid": data_source_uid
            },
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)
        
        # Celery 태스크 비동기 실행
        create_grafana_logs_dashboard.apply_async(
            args=(saved_result.id, user_id, user_name, folder_uid, data_source_uid),
            task_id=saved_result.task_id
        )
        
        print(f"로그 대시보드 생성 요청: user_id={user_id}, folder_uid={folder_uid}")
        return saved_result.id

    def _find_folder_uid_for_user(self, user_id: str) -> Optional[str]:
        """
        사용자 폴더 UID 검색 (내부 메서드)
        """
        try:
            from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
            # 해당 사용자의 가장 최근 폴더 생성 태스크 조회
            recent_folder_task = TaskResultModel.objects.filter(
                task_name="create_grafana_folder",
                result__contains=user_id,
                status=TaskStatus.SUCCESS
            ).order_by('-date_done').first()
            
            if recent_folder_task and recent_folder_task.result:
                result_data = recent_folder_task.result
                if isinstance(result_data, dict) and 'uid' in result_data:
                    return result_data['uid']
            
            # DB에서 찾지 못한 경우 Grafana API 사용
            from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
            api = GrafanaAPI()
            folders = api.get_folders()
            
            folder_pattern = f"User_{user_id}_"
            for folder in folders:
                if folder_pattern in folder.get('title', ''):
                    return folder.get('uid')
        except Exception as e:
            print(f"폴더 UID 검색 실패: {str(e)}")
        
        return None

    """
    그라파나 대시보드 구성 흐름
    
    1. 사용자 폴더 생성
       - create_user_folder() 호출
       - TaskResult에서 성공 여부 및 folder_uid 확인
    
    2. 서비스 계정 생성
       - create_service_account() 호출
       - TaskResult에서 성공 여부 및 service_account_id 확인
    
    3. 서비스 토큰 생성
       - create_service_token() 호출 (service_account_id 필요)
       - TaskResult에서 성공 여부 및 token 확인
    
    4. 폴더 권한 설정
       - set_folder_permissions() 호출 (folder_uid, service_account_id 필요)
       - TaskResult에서 성공 여부 확인
    
    5. 대시보드 생성
       - create_dashboard() 호출 (folder_uid 필요)
       - TaskResult에서 성공 여부 및 dashboard_uid 확인
    
    이전 단계의 결과가 다음 단계에 필요
    """