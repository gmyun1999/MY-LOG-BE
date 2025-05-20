from django.core.management.base import BaseCommand
from monitoring_provisioner.infra.celery.executor.grafana_executor import GrafanaExecutor
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
import time


class Command(BaseCommand):
    help = "Test Grafana integration with Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=str, default="test_user_123")
        parser.add_argument('--user-name', type=str, default="Test User")
        parser.add_argument('--dashboard-title', type=str, default="Test Dashboard")
        parser.add_argument('--action', type=str, choices=['folder', 'account', 'token', 'dashboard', 'permissions', 'all', 'sequence'], default='all')
        parser.add_argument('--wait-for-completion', action='store_true', help='Wait for tasks to complete before proceeding')

    def handle(self, *args, **options):
        executor = GrafanaExecutor()
        user_id = options['user_id']
        user_name = options['user_name']
        dashboard_title = options['dashboard_title']
        action = options['action']
        wait_for_completion = options['wait_for_completion']
        
        self.stdout.write(self.style.SUCCESS(f"테스트 시작: {action} 작업"))
        
        task_ids = {}
        
        # 순차적 실행 옵션
        if action == 'sequence':
            self.stdout.write("폴더 생성 → 서비스 계정 → 서비스 토큰 → 권한 설정 → 대시보드 순차 실행 중...")
            
            # 1. 폴더 생성
            self.stdout.write("1. 폴더 생성 요청 중...")
            folder_task_id = executor.create_user_folder(user_id, user_name)
            self.stdout.write(self.style.SUCCESS(f"폴더 생성 태스크 등록 완료. Task ID: {folder_task_id}"))
            
            if wait_for_completion:
                self.wait_for_task_completion(folder_task_id)
                folder_uid = self.get_folder_uid_from_task(folder_task_id)
            else:
                # 폴더 생성에 시간이 필요하므로 잠시 대기
                time.sleep(2)
                folder_uid = self.get_folder_uid_from_task(folder_task_id)
            
            # 2. 서비스 계정 생성
            self.stdout.write("2. 서비스 계정 생성 요청 중...")
            account_task_id = executor.create_service_account(user_id, "Viewer")
            self.stdout.write(self.style.SUCCESS(f"서비스 계정 생성 태스크 등록 완료. Task ID: {account_task_id}"))
            
            if wait_for_completion:
                self.wait_for_task_completion(account_task_id)
                service_account_id = self.get_service_account_id_from_task(account_task_id)
            else:
                # 서비스 계정 생성에 시간이 필요하므로 잠시 대기
                time.sleep(2)
                service_account_id = self.get_service_account_id_from_task(account_task_id)
            
            # 3. 서비스 토큰 생성
            service_token = None
            if service_account_id:
                self.stdout.write(f"3. 서비스 토큰 생성 요청 중... (서비스 계정 ID: {service_account_id})")
                token_task_id = executor.create_service_token(service_account_id, user_id)
                self.stdout.write(self.style.SUCCESS(f"서비스 토큰 생성 태스크 등록 완료. Task ID: {token_task_id}"))
                
                if wait_for_completion:
                    self.wait_for_task_completion(token_task_id)
                    service_token = self.get_service_token_from_task(token_task_id)
                else:
                    # 토큰 생성에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                    service_token = self.get_service_token_from_task(token_task_id)
                
                # 태스크 ID 정보 추가
                task_ids['token'] = token_task_id
            else:
                self.stdout.write(self.style.WARNING("서비스 계정 ID를 가져올 수 없어 토큰 생성을 진행하지 않습니다."))
            
            # 4. 폴더 권한 설정
            if folder_uid and service_account_id:
                self.stdout.write(f"4. 폴더 권한 설정 요청 중... (폴더 UID: {folder_uid}, 서비스 계정 ID: {service_account_id})")
                permission_task_id = executor.set_folder_permissions(folder_uid, service_account_id)
                self.stdout.write(self.style.SUCCESS(f"폴더 권한 설정 태스크 등록 완료. Task ID: {permission_task_id}"))
                
                if wait_for_completion:
                    self.wait_for_task_completion(permission_task_id)
                else:
                    # 권한 설정에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                
                # 태스크 ID 정보 추가
                task_ids['permission'] = permission_task_id
            else:
                self.stdout.write(self.style.WARNING("폴더 UID 또는 서비스 계정 ID를 가져올 수 없어 권한 설정을 진행하지 않습니다."))
            
            # 5. 대시보드 생성
            dashboard_uid = None
            if folder_uid:
                self.stdout.write(f"5. 대시보드 생성 요청 중... (폴더 UID: {folder_uid})")
                dashboard_task_id = executor.create_dashboard(
                    user_id=user_id,
                    title=dashboard_title,
                    panels=[
                        {
                            "id": 1,
                            "type": "graph",
                            "title": "CPU Usage",
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                        }
                    ],
                    folder_uid=folder_uid  # 폴더 UID 명시적 전달
                )
                self.stdout.write(self.style.SUCCESS(f"대시보드 생성 태스크 등록 완료. Task ID: {dashboard_task_id}"))
                
                if wait_for_completion:
                    self.wait_for_task_completion(dashboard_task_id)
                    dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
                else:
                    # 대시보드 생성에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                    dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
                
                # 대시보드 정보 추가
                task_ids['dashboard'] = dashboard_task_id
            else:
                self.stdout.write(self.style.WARNING("폴더 UID를 가져올 수 없어 대시보드를 생성하지 않습니다."))
            
            # 6. 인증된 URL 생성
            if dashboard_uid and service_token:
                grafana_api = GrafanaAPI()
                # base_url에서 마지막 슬래시 제거
                base_url = grafana_api.base_url.rstrip('/')
                authenticated_url = f"{base_url}/d/{dashboard_uid}/test-dashboard?orgId=1&auth_token={service_token}"
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("접근 가능한 URL이 생성되었습니다:"))
                self.stdout.write(self.style.SUCCESS(authenticated_url))
                self.stdout.write(self.style.SUCCESS("이 URL을 사용하면 로그인 없이 대시보드에 접근할 수 있습니다."))
            
            # 태스크 ID 정보 추가
            task_ids['folder'] = folder_task_id
            task_ids['account'] = account_task_id
            
        elif action in ['folder', 'all']:
            self.stdout.write("폴더 생성 요청 중...")
            task_id = executor.create_user_folder(user_id, user_name)
            task_ids['folder'] = task_id
            self.stdout.write(self.style.SUCCESS(f"폴더 생성 태스크 등록 완료. Task ID: {task_id}"))
        
        elif action in ['account', 'all']:
            self.stdout.write("서비스 계정 생성 요청 중...")
            task_id = executor.create_service_account(user_id, "Viewer")
            task_ids['account'] = task_id
            self.stdout.write(self.style.SUCCESS(f"서비스 계정 생성 태스크 등록 완료. Task ID: {task_id}"))
        
        elif action in ['token']:
            self.stdout.write("서비스 토큰 생성 요청 중...")
            # 서비스 계정 ID 찾기
            account_name = f"service-{user_id}"
            service_account_id = self.find_service_account_id(account_name)
            if not service_account_id:
                self.stdout.write(self.style.ERROR(f"서비스 계정 {account_name}을 찾을 수 없습니다."))
                return
            
            self.stdout.write(f"서비스 계정 ID: {service_account_id}")
            task_id = executor.create_service_token(service_account_id, user_id)
            task_ids['token'] = task_id
            self.stdout.write(self.style.SUCCESS(f"서비스 토큰 생성 태스크 등록 완료. Task ID: {task_id}"))
            
            if wait_for_completion:
                self.wait_for_task_completion(task_id)
                token = self.get_service_token_from_task(task_id)
                if token:
                    self.stdout.write(self.style.SUCCESS(f"생성된 서비스 토큰: {token}"))
        
        elif action in ['permissions']:
            self.stdout.write("폴더 권한 설정 요청 중...")
            # 폴더 UID 찾기
            folder_uid = self.find_folder_uid_for_user(user_id)
            if not folder_uid:
                self.stdout.write(self.style.ERROR(f"사용자 {user_id}의 폴더를 찾을 수 없습니다."))
                return
            
            # 서비스 계정 ID 찾기
            account_name = f"service-{user_id}"
            service_account_id = self.find_service_account_id(account_name)
            if not service_account_id:
                self.stdout.write(self.style.ERROR(f"서비스 계정 {account_name}을 찾을 수 없습니다."))
                return
            
            self.stdout.write(f"폴더 UID: {folder_uid}, 서비스 계정 ID: {service_account_id}")
            task_id = executor.set_folder_permissions(folder_uid, service_account_id)
            task_ids['permissions'] = task_id
            self.stdout.write(self.style.SUCCESS(f"폴더 권한 설정 태스크 등록 완료. Task ID: {task_id}"))
        
        elif action in ['dashboard', 'all']:
            self.stdout.write("대시보드 생성 요청 중...")
            
            # 폴더 UID 찾기 시도
            folder_uid = self.find_folder_uid_for_user(user_id)
            if folder_uid:
                self.stdout.write(f"사용자 {user_id}의 폴더 UID 발견: {folder_uid}")
            
            task_id = executor.create_dashboard(
                user_id=user_id,
                title=dashboard_title,
                panels=[
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "CPU Usage",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    }
                ],
                folder_uid=folder_uid  # 발견된 경우 전달
            )
            task_ids['dashboard'] = task_id
            self.stdout.write(self.style.SUCCESS(f"대시보드 생성 태스크 등록 완료. Task ID: {task_id}"))
        
        self.stdout.write(self.style.SUCCESS(f"테스트 완료. 등록된 태스크 ID: {task_ids}"))
    
    def wait_for_task_completion(self, task_id, timeout=30):
        """태스크가 완료될 때까지 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                task = TaskResultModel.objects.get(id=task_id)
                if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]:
                    self.stdout.write(f"태스크 {task_id} 완료. 상태: {task.status}")
                    return task.status == TaskStatus.SUCCESS
                time.sleep(1)
            except TaskResultModel.DoesNotExist:
                time.sleep(1)
        
        self.stdout.write(self.style.WARNING(f"태스크 {task_id} 시간 초과. 계속 진행합니다."))
        return False
    
    def get_folder_uid_from_task(self, task_id):
        """태스크 결과에서 폴더 UID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and 'uid' in result:
                    return result['uid']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 추출 실패: {str(e)}"))
        return None
    
    def get_service_account_id_from_task(self, task_id):
        """태스크 결과에서 서비스 계정 ID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and 'id' in result:
                    return result['id']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 계정 ID 추출 실패: {str(e)}"))
        return None
    
    def get_service_token_from_task(self, task_id):
        """태스크 결과에서 서비스 토큰 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and 'key' in result:
                    return result['key']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 토큰 추출 실패: {str(e)}"))
        return None
    
    def get_dashboard_uid_from_task(self, task_id):
        """태스크 결과에서 대시보드 UID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and 'uid' in result:
                    return result['uid']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"대시보드 UID 추출 실패: {str(e)}"))
        return None
    
    def find_folder_uid_for_user(self, user_id):
        """사용자의 폴더 UID 검색"""
        try:
            # 최근 폴더 생성 태스크 조회
            recent_folder_task = TaskResultModel.objects.filter(
                task_name="create_grafana_folder",
                result__contains=user_id,
                status=TaskStatus.SUCCESS
            ).order_by('-date_done').first()
            
            if recent_folder_task and recent_folder_task.result:
                result_data = recent_folder_task.result
                if isinstance(result_data, dict) and 'uid' in result_data:
                    return result_data['uid']
            
            # DB에서 찾지 못한 경우 그라파나 API 사용
            from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
            api = GrafanaAPI()
            folders = api.get_folders()
            
            # 폴더 이름 패턴
            folder_pattern = f"User_{user_id}_"
            
            for folder in folders:
                if folder_pattern in folder.get('title', ''):
                    return folder.get('uid')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 검색 실패: {str(e)}"))
        
        return None
    
    def find_service_account_id(self, account_name):
        """서비스 계정 ID 검색"""
        try:
            # 최근 서비스 계정 생성 태스크 조회
            recent_account_task = TaskResultModel.objects.filter(
                task_name="create_grafana_service_account",
                result__contains=account_name,
                status=TaskStatus.SUCCESS
            ).order_by('-date_done').first()
            
            if recent_account_task and recent_account_task.result:
                result_data = recent_account_task.result
                if isinstance(result_data, dict) and 'id' in result_data:
                    return result_data['id']
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 계정 ID 검색 실패: {str(e)}"))
        
        return None