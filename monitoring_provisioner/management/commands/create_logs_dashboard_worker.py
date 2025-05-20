# monitoring_provisioner/management/commands/create_logs_dashboard_worker.py

from django.core.management.base import BaseCommand
from typing import Optional, Dict, Any, List
from monitoring_provisioner.infra.celery.executor.grafana_executor import GrafanaExecutor
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
import time
import uuid


class Command(BaseCommand):
    help = "Create Elasticsearch logs dashboard for a user"

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=str, required=True, help='User ID to create dashboard for')
        parser.add_argument('--user-name', type=str, help='User name for dashboard title')
        parser.add_argument('--data-source-uid', type=str, default="Elasticsearch", help='Elasticsearch data source UID')
        parser.add_argument('--wait-for-completion', action='store_true', help='Wait for tasks to complete before proceeding')
        parser.add_argument('--make-public', action='store_true', help='Create public dashboard link after creation')
        parser.add_argument('--folder-uid', type=str, help='Specific folder UID to create dashboard in')
        parser.add_argument('--dashboard-title', type=str, help='Custom dashboard title')
        parser.add_argument('--dashboard-uid', type=str, help='Custom dashboard UID (if None, one will be generated)')

    def handle(self, *args, **options):
        executor = GrafanaExecutor()
        user_id = options['user_id']
        user_name = options['user_name'] or f"User {user_id}"
        data_source_uid = options['data_source_uid']
        wait_for_completion = options['wait_for_completion']
        make_public = options['make_public']
        specific_folder_uid = options.get('folder_uid')
        dashboard_title = options.get('dashboard_title')
        dashboard_uid = options.get('dashboard_uid')
        
        # 대시보드 UID가 지정되지 않은 경우 생성
        if not dashboard_uid:
            dashboard_uid = f"logs-dashboard-{user_id}-{uuid.uuid4().hex[:8]}"
        
        self.stdout.write(self.style.SUCCESS(f"로그 대시보드 생성 시작: 사용자 {user_id}"))
        
        # 1. 폴더 UID 결정 (사용자 지정 또는 자동 생성)
        if specific_folder_uid:
            folder_uid = specific_folder_uid
            self.stdout.write(self.style.SUCCESS(f"지정된 폴더 UID 사용: {folder_uid}"))
        else:
            # 기존 로직: 사용자 폴더 확인 및 생성
            folder_uid = self.find_folder_uid_for_user(user_id)
            
            if not folder_uid:
                self.stdout.write(self.style.WARNING(f"사용자 {user_id}의 폴더를 찾을 수 없습니다. 새 폴더를 생성합니다."))
                folder_task_id = executor.create_user_folder(user_id, user_name)
                
                if wait_for_completion:
                    self.wait_for_task_completion(folder_task_id)
                    folder_uid = self.get_folder_uid_from_task(folder_task_id)
                else:
                    time.sleep(2)  # 폴더 생성 시간 대기
                    folder_uid = self.get_folder_uid_from_task(folder_task_id)
        
        self.stdout.write(self.style.SUCCESS(f"사용자 폴더 UID: {folder_uid}"))
        
        # 2. 로그 대시보드 생성
        self.stdout.write(f"로그 대시보드 생성 요청 중 (폴더 UID: {folder_uid}, 대시보드 UID: {dashboard_uid})...")
        
        # 대시보드 제목 설정
        if dashboard_title:
            self.stdout.write(f"커스텀 대시보드 제목 사용: {dashboard_title}")
        
        # 대시보드 생성 요청
        dashboard_task_id = executor.create_logs_dashboard(
            user_id=user_id,
            user_name=user_name,
            folder_uid=folder_uid,
            data_source_uid=data_source_uid,
            dashboard_title=dashboard_title,
            dashboard_uid=dashboard_uid
        )
        
        if wait_for_completion:
            self.wait_for_task_completion(dashboard_task_id)
            dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
        else:
            time.sleep(2)  # 대시보드 생성 시간 대기
            dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
        
        if not dashboard_uid:
            self.stdout.write(self.style.ERROR("로그 대시보드 생성 실패!"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"로그 대시보드 생성 완료. UID: {dashboard_uid}"))
        
        # 3. 퍼블릭 대시보드 설정 (선택 사항)
        public_dashboard_url = None
        if make_public and dashboard_uid:
            self.stdout.write(self.style.SUCCESS("퍼블릭 대시보드 설정 중..."))
            public_dashboard_url = self.create_or_get_public_dashboard(
                executor=executor,
                dashboard_uid=dashboard_uid,
                wait_for_completion=wait_for_completion
            )
        
        # 4. URL 및 결과 표시
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== 로그 대시보드 생성 결과 ==="))
        self.stdout.write(self.style.SUCCESS(f"사용자 ID: {user_id}"))
        dashboard_title = dashboard_title or f"로그 대시보드 - {user_name}"
        self.stdout.write(self.style.SUCCESS(f"대시보드 제목: {dashboard_title}"))
        self.stdout.write(self.style.SUCCESS(f"폴더 UID: {folder_uid}"))
        self.stdout.write(self.style.SUCCESS(f"대시보드 UID: {dashboard_uid}"))
        
        # 대시보드 URL 생성
        grafana_api = GrafanaAPI()
        dashboard_url = f"{grafana_api.base_url}/d/{dashboard_uid}"
        self.stdout.write(self.style.SUCCESS(f"대시보드 URL: {dashboard_url}"))
        
        if public_dashboard_url:
            self.stdout.write(self.style.SUCCESS(f"퍼블릭 대시보드 URL: {public_dashboard_url}"))
        
        self.stdout.write(self.style.SUCCESS("=== 작업 완료 ==="))

    def create_or_get_public_dashboard(self, executor, dashboard_uid, wait_for_completion):
        """
        대시보드의 퍼블릭 링크 생성 또는 기존 퍼블릭 링크 조회
        """
        grafana_api = GrafanaAPI()
        
        try:
            # 기존 퍼블릭 대시보드 확인 시도
            existing_public = self.get_existing_public_dashboard(dashboard_uid)
            
            if existing_public:
                self.stdout.write(self.style.SUCCESS(f"이미 퍼블릭 대시보드가 존재합니다. 기존 URL을 사용합니다."))
                return grafana_api.generate_public_dashboard_url(existing_public)
            
            # 없으면 새로 생성
            public_dashboard_task_id = executor.create_public_dashboard(dashboard_uid)
            
            if wait_for_completion:
                self.wait_for_task_completion(public_dashboard_task_id)
                public_dashboard_result = self.get_public_dashboard_result_from_task(public_dashboard_task_id)
            else:
                time.sleep(2)  # 퍼블릭 설정 시간 대기
                public_dashboard_result = self.get_public_dashboard_result_from_task(public_dashboard_task_id)
            
            if public_dashboard_result and 'accessToken' in public_dashboard_result:
                return grafana_api.generate_public_dashboard_url(public_dashboard_result)
            
            # 대시보드가 이미 퍼블릭인 경우
            if public_dashboard_task_id:
                task = TaskResultModel.objects.get(id=public_dashboard_task_id)
                if task.status == TaskStatus.FAILURE and "Dashboard is already public" in str(task.traceback):
                    self.stdout.write(self.style.WARNING("대시보드가 이미 퍼블릭으로 설정되어 있습니다. 기존 URL 확인 중..."))
                    
                    # 다시 한번 퍼블릭 대시보드 정보 조회 시도
                    try:
                        time.sleep(1)  # 짧은 대기 시간
                        existing_public = self.get_existing_public_dashboard(dashboard_uid)
                        if existing_public:
                            return grafana_api.generate_public_dashboard_url(existing_public)
                    except:
                        pass
            
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"퍼블릭 대시보드 생성 오류: {str(e)}"))
            return None
            
    def get_existing_public_dashboard(self, dashboard_uid):
        """
        이미 존재하는 퍼블릭 대시보드 정보 조회
        """
        try:
            grafana_api = GrafanaAPI()
            public_dashboards = grafana_api.get_public_dashboards_for_dashboard(dashboard_uid)
            
            if public_dashboards and len(public_dashboards) > 0:
                return public_dashboards[0]
            return None
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"퍼블릭 대시보드 조회 오류: {str(e)}"))
            return None
    
    def find_folder_uid_for_user(self, user_id: str) -> Optional[str]:
        """
        사용자 ID로 폴더 UID 검색
        """
        try:
            # DB에서 폴더 검색
            recent_folder_task = TaskResultModel.objects.filter(
                task_name="create_grafana_folder",
                result__contains=user_id,
                status=TaskStatus.SUCCESS
            ).order_by('-date_done').first()
            
            if recent_folder_task and recent_folder_task.result:
                result_data = recent_folder_task.result
                if isinstance(result_data, dict) and 'uid' in result_data:
                    return result_data['uid']
            
            # Grafana API 직접 호출
            grafana_api = GrafanaAPI()
            folders = grafana_api.get_folders()
            
            folder_pattern = f"User_{user_id}_"
            for folder in folders:
                if folder_pattern in folder.get('title', ''):
                    return folder.get('uid')
                    
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 검색 오류: {str(e)}"))
            return None
    
    def wait_for_task_completion(self, task_id: str, max_wait_time: int = 30, check_interval: int = 2) -> bool:
        """
        태스크 완료 대기
        """
        self.stdout.write(f"태스크 {task_id} 완료 대기 중...")
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                task = TaskResultModel.objects.get(id=task_id)
                if task.status == TaskStatus.SUCCESS:
                    self.stdout.write(self.style.SUCCESS(f"태스크 {task_id} 성공 완료!"))
                    return True
                elif task.status == TaskStatus.FAILURE:
                    self.stdout.write(self.style.ERROR(f"태스크 {task_id} 실패: {task.traceback}"))
                    return False
                else:
                    self.stdout.write(f"태스크 {task_id} 상태: {task.status}, 대기 중...")
            except TaskResultModel.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"태스크 {task_id}를 찾을 수 없습니다."))
                return False
            
            time.sleep(check_interval)
            elapsed_time += check_interval
        
        self.stdout.write(self.style.WARNING(f"태스크 {task_id} 최대 대기 시간 초과!"))
        return False
    
    def get_folder_uid_from_task(self, task_id: str) -> Optional[str]:
        """
        태스크 결과에서 폴더 UID 추출
        """
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result_data = task.result
                if isinstance(result_data, dict) and 'uid' in result_data:
                    return result_data['uid']
            return None
        except (TaskResultModel.DoesNotExist, Exception) as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 조회 오류: {str(e)}"))
            return None
    
    def get_dashboard_uid_from_task(self, task_id: str) -> Optional[str]:
        """
        태스크 결과에서 대시보드 UID 추출
        """
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result_data = task.result
                if isinstance(result_data, dict):
                    # 그라파나 API의 대시보드 생성 응답 구조에 맞게 처리
                    if 'uid' in result_data:
                        return result_data['uid']
                    elif 'dashboard' in result_data and 'uid' in result_data['dashboard']:
                        return result_data['dashboard']['uid']
                    elif 'dashboardId' in result_data:
                        # UID가 없는 경우 ID로 재조회 시도
                        dashboard_id = result_data['dashboardId']
                        return dashboard_id
            return None
        except (TaskResultModel.DoesNotExist, Exception) as e:
            self.stdout.write(self.style.ERROR(f"대시보드 UID 조회 오류: {str(e)}"))
            return None
    
    def get_public_dashboard_result_from_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        태스크 결과에서 퍼블릭 대시보드 정보 추출
        """
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result_data = task.result
                if isinstance(result_data, dict):
                    return result_data
            return None
        except (TaskResultModel.DoesNotExist, Exception) as e:
            self.stdout.write(self.style.ERROR(f"퍼블릭 대시보드 정보 조회 오류: {str(e)}"))
            return None