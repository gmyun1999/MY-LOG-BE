import uuid
from django.utils import timezone
from monitoring_provisioner.infra.celery.tasks.utils import locking_task
from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel

# 태스크 성공 시 상태 업데이트 함수
def update_task_success(task_result_id, result):
    try:
        TaskResultModel.objects.filter(id=task_result_id).update(
            status=TaskStatus.SUCCESS,
            result=result,
            date_done=timezone.now()
        )
        print(f"태스크 {task_result_id} 상태 업데이트: SUCCESS")
    except Exception as e:
        print(f"태스크 상태 업데이트 실패: {str(e)}")

@locking_task(max_retries=3, default_retry_delay=5)
def create_grafana_folder(self, task_result_id, folder_name):
    """
    그라파나 폴더 생성 태스크
    첫 번째 인자로 task_result_id를 유지하여 시그널 핸들러와 호환성 유지
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        # 태스크 정보 조회
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    # 그라파나 API 호출
    grafana_api = GrafanaAPI()
    result = grafana_api.create_folder(folder_name)
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def create_grafana_service_account(self, task_result_id, name, role="Viewer"):
    """
    그라파나 서비스 계정 생성 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    print(f"서비스 계정 생성 요청: URL={grafana_api.base_url}/api/serviceaccounts, 데이터={{'name': '{name}', 'role': '{role}'}}")
    result = grafana_api.create_service_account(name, role)
    print(f"서비스 계정 생성 응답: 상태 코드=201, 응답={result}")
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def create_grafana_service_token(self, task_result_id, service_account_id, token_name):
    """
    그라파나 서비스 토큰 생성 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    print(f"서비스 토큰 생성 요청: 계정 ID={service_account_id}, 토큰명={token_name}")
    result = grafana_api.create_service_token(service_account_id, token_name)
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def set_grafana_folder_permissions(self, task_result_id, folder_uid, service_account_id):
    """
    그라파나 폴더 권한 설정 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    result = grafana_api.set_folder_permissions(folder_uid, service_account_id)
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def create_grafana_dashboard(self, task_result_id, dashboard_data, folder_uid=None):
    """
    그라파나 대시보드 생성 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
        
        # 폴더 UID가 None이고 태스크 데이터에 있다면 사용
        if folder_uid is None and 'folder_uid' in task_data:
            folder_uid = task_data.get('folder_uid')
            print(f"태스크 데이터에서 폴더 UID 사용: {folder_uid}")
        
        # 여기에 추가: 사용자 ID로 폴더 검색
        if folder_uid is None and 'user_id' in task_data:
            user_id = task_data.get('user_id')
            try:
                # 그라파나 API에서 폴더 목록 조회
                grafana_api = GrafanaAPI()
                folders = grafana_api.get_folders()
                
                # 폴더 이름 패턴
                folder_pattern = f"User_{user_id}_"
                
                for folder in folders:
                    if folder_pattern in folder.get('title', ''):
                        folder_uid = folder.get('uid')
                        print(f"그라파나 API에서 찾은 폴더 UID: {folder_uid}")
                        break
            except Exception as e:
                print(f"폴더 검색 오류: {str(e)}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    print(f"대시보드 생성 시작: dashboard_data={dashboard_data}, folder_uid={folder_uid}")
    
    grafana_api = GrafanaAPI()
    result = grafana_api.create_dashboard(dashboard_data, folder_uid)
    
    print(f"대시보드 생성 결과: {result}")
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def get_grafana_dashboard(self, task_result_id, uid):
    """
    그라파나 대시보드 조회 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    result = grafana_api.get_dashboard(uid)
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def get_grafana_folders(self, task_result_id):
    """
    그라파나 폴더 목록 조회 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    result = grafana_api.get_folders()
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result

@locking_task(max_retries=3, default_retry_delay=5)
def create_grafana_public_dashboard(self, task_result_id, dashboard_uid):
    """
    그라파나 퍼블릭 대시보드 생성 태스크
    """
    print(f"태스크 {task_result_id} 실행 중...")
    
    try:
        task_result = TaskResultModel.objects.get(id=task_result_id)
        task_data = task_result.result or {}
        print(f"태스크 데이터: {task_data}")
    except TaskResultModel.DoesNotExist:
        print(f"태스크 정보 조회 실패: TaskResultModel matching query does not exist.")
    
    grafana_api = GrafanaAPI()
    result = grafana_api.create_public_dashboard(dashboard_uid)
    
    # 성공 시 상태 업데이트
    update_task_success(task_result_id, result)
    
    return result