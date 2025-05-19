import uuid
from django.utils import timezone
from monitoring_provisioner.infra.celery.tasks.utils import locking_task
from monitoring_provisioner.infra.repository.grafana_repo import GrafanaRepository
from monitoring_provisioner.infra.repository.task_result_repo import TaskResultRepository
from monitoring_provisioner.domain.grafana_dashboard import GrafanaDashboard
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel


@locking_task(max_retries=3, default_retry_delay=5)
def send_dashboard_creation_request(self, task_result_id: str):
    """
    대시보드 생성 요청 처리 태스크
    """
    # 태스크 결과 레코드 조회
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
    except TaskResultModel.DoesNotExist:
        return {"error": "Task result not found"}
    
    grafana_repo = GrafanaRepository()
    
    try:
        user_id = task_data.get("user_id")
        title = task_data.get("title", f"Dashboard for User {user_id}")
        folder_uid = task_data.get("folder_uid")
        
        # 대시보드 도메인 객체 생성
        dashboard = GrafanaDashboard(
            uid=f"user-{user_id}-{uuid.uuid4().hex[:8]}",
            title=title,
            user_id=user_id,
            folder_uid=folder_uid,
            tags=["auto-generated", f"user-{user_id}"],
            panels=task_data.get("panels", [
                # 기본 패널 설정
                {
                    "id": 1,
                    "type": "graph",
                    "title": "샘플 그래프",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                }
            ])
        )
        
        # 대시보드 생성
        created_dashboard = grafana_repo.create_dashboard(dashboard)
        
        # 서비스 계정 토큰으로 대시보드 URL 생성
        service_token = task_data.get("service_token")
        dashboard_url = None
        
        if service_token:
            dashboard_url = f"{created_dashboard.url}?auth_token={service_token}"
        
        return {
            "dashboard_uid": created_dashboard.uid,
            "title": created_dashboard.title,
            "url": dashboard_url or created_dashboard.url
        }
    
    except Exception as e:
        self.retry(exc=e)


@locking_task(max_retries=3, default_retry_delay=5)
def send_user_folder_creation_request(self, task_result_id: str):
    """
    사용자 폴더 생성 요청 처리 태스크
    """
    print(f"사용자 폴더 생성 태스크 시작: {task_result_id}")
    
    # 태스크 결과 레코드 조회
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 결과를 찾을 수 없음: {task_result_id}")
        return {"error": "Task result not found"}
    
    grafana_repo = GrafanaRepository()
    result = {}
    
    try:
        user_id = task_data.get("user_id")
        user_name = task_data.get("user_name", f"User {user_id}")
        
        # 1. 사용자 폴더 생성
        print(f"폴더 생성 시도: {user_name}'s Folder (user_{user_id})")
        folder_uid = grafana_repo.create_folder(user_id, f"{user_name}'s Folder")
        result["folder_uid"] = folder_uid
        print(f"폴더 생성 성공: {folder_uid}")
        
        # 2. 서비스 계정 생성 (이 부분이 실패할 수 있음)
        service_account_id = None
        service_token = None
        
        try:
            print(f"서비스 계정 생성 시도: service-{user_id}")
            service_account = grafana_repo.create_service_account(
                name=f"service-{user_id}",
                role="Viewer"
            )
            
            print(f"서비스 계정 응답: {service_account}")
            
            # 그라파나 12.0.0에서는 "id" 필드로 반환
            if isinstance(service_account, dict):
                service_account_id = service_account.get("id")
                
                if not service_account_id:
                    # 또는 "uid" 필드로 반환될 수 있음
                    service_account_id = service_account.get("uid")
                
                result["service_account_id"] = service_account_id
                print(f"서비스 계정 생성 성공: {service_account_id}")
                
                # 3. 서비스 계정 토큰 생성
                print(f"서비스 계정 토큰 생성 시도: token-{user_id}")
                token_result = grafana_repo.create_service_token(
                    service_account_id=service_account_id,
                    token_name=f"token-{user_id}"
                )
                
                print(f"토큰 생성 응답: {token_result}")
                
                if isinstance(token_result, dict):
                    service_token = token_result.get("key")
                    result["service_token"] = service_token
                    print(f"서비스 계정 토큰 생성 성공")
                    
                    # 4. 폴더 권한 설정
                    if folder_uid and service_account_id:
                        print(f"폴더 권한 설정 시도: folder={folder_uid}, account={service_account_id}")
                        grafana_repo.set_folder_permissions(folder_uid, service_account_id)
                        print("폴더 권한 설정 성공")
        
        except Exception as e:
            print(f"서비스 계정 관련 작업 중 오류: {str(e)}")
            # 서비스 계정 생성 실패해도 폴더 UID는 반환
            
        return result
    
    except Exception as e:
        print(f"사용자 폴더 생성 오류: {str(e)}")
        self.retry(exc=e)