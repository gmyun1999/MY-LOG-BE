import json
import time

from django.core.management.base import BaseCommand

from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.celery.task_executor.grafana_executor import (
    GrafanaTaskExecutor,
)
from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel


class Command(BaseCommand):
    help = "Add a dashboard to a user's folder and make it public"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id", type=str, required=True, help="User ID to add dashboard for"
        )
        parser.add_argument(
            "--dashboard-title",
            type=str,
            default="New Dashboard",
            help="Title of the dashboard",
        )
        parser.add_argument(
            "--dashboard-template",
            type=str,
            help="Path to JSON file with dashboard template",
        )
        parser.add_argument("--wait", action="store_true", help="Wait for completion")

    def handle(self, *args, **options):
        user_id = options["user_id"]
        dashboard_title = options["dashboard_title"]
        dashboard_template = options["dashboard_template"]
        wait = options["wait"]

        executor = GrafanaTaskExecutor()

        self.stdout.write(
            self.style.SUCCESS(
                f"대시보드 추가 시작: 사용자 {user_id}, 제목 '{dashboard_title}'"
            )
        )

        # 1. 사용자 폴더 UID 찾기
        folder_uid = self.find_folder_uid_for_user(user_id)

        if not folder_uid:
            self.stdout.write(
                self.style.WARNING(
                    f"사용자 {user_id}의 폴더를 찾을 수 없습니다. 새 폴더를 생성합니다."
                )
            )
            folder_task_id = executor.dispatch_create_user_folder(
                user_id, f"User {user_id}"
            )

            if wait:
                self.wait_for_task_completion(folder_task_id)
                folder_uid = self.get_folder_uid_from_task(folder_task_id)
            else:
                time.sleep(2)  # 폴더 생성 시간 대기
                folder_uid = self.get_folder_uid_from_task(folder_task_id)

        self.stdout.write(self.style.SUCCESS(f"사용자 폴더 UID: {folder_uid}"))

        # 2. 대시보드 패널 준비 (템플릿 또는 기본값)
        panels = []

        if dashboard_template:
            try:
                with open(dashboard_template, "r") as f:
                    template_data = json.load(f)
                    if "panels" in template_data:
                        panels = template_data["panels"]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"템플릿에서 {len(panels)}개의 패널을 로드했습니다."
                            )
                        )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"템플릿 로드 오류: {str(e)}"))
                # 기본 패널 사용
                panels = [
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "CPU Usage",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                    }
                ]
        else:
            # 기본 패널
            panels = [
                {
                    "id": 1,
                    "type": "graph",
                    "title": "CPU Usage",
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                }
            ]

        # 3. 대시보드 생성
        self.stdout.write(
            self.style.SUCCESS(f"대시보드 생성 요청 중 (폴더 UID: {folder_uid})...")
        )
        dashboard_task_id = executor.create_dashboard(
            user_id=user_id, title=dashboard_title, panels=panels, folder_uid=folder_uid
        )

        dashboard_uid = None
        if wait:
            self.wait_for_task_completion(dashboard_task_id)
            dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
        else:
            time.sleep(2)  # 대시보드 생성 시간 대기
            dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)

        if not dashboard_uid:
            self.stdout.write(self.style.ERROR("대시보드 생성 실패!"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"대시보드 생성 완료. UID: {dashboard_uid}")
        )

        # 4. 퍼블릭 대시보드 설정
        self.stdout.write(self.style.SUCCESS("퍼블릭 대시보드 설정 중..."))
        public_dashboard_task_id = executor.dispatch_create_public_dashboard(
            dashboard_uid
        )

        if wait:
            self.wait_for_task_completion(public_dashboard_task_id)
            public_dashboard_result = self.get_public_dashboard_result_from_task(
                public_dashboard_task_id
            )
        else:
            time.sleep(2)  # 퍼블릭 설정 시간 대기
            public_dashboard_result = self.get_public_dashboard_result_from_task(
                public_dashboard_task_id
            )

        # 5. URL 및 결과 표시
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== 대시보드 생성 결과 ==="))
        self.stdout.write(self.style.SUCCESS(f"사용자 ID: {user_id}"))
        self.stdout.write(self.style.SUCCESS(f"폴더 UID: {folder_uid}"))
        self.stdout.write(self.style.SUCCESS(f"대시보드 UID: {dashboard_uid}"))
        self.stdout.write(self.style.SUCCESS(f"대시보드 제목: {dashboard_title}"))

        if public_dashboard_result and "accessToken" in public_dashboard_result:
            grafana_api = GrafanaAPI()
            base_url = grafana_api.base_url.rstrip("/")

            # 대시보드 URL
            dashboard_url = (
                f"{base_url}/d/{dashboard_uid}/{self.slugify(dashboard_title)}?orgId=1"
            )

            # 퍼블릭 URL
            public_url = (
                f"{base_url}/public-dashboards/{public_dashboard_result['accessToken']}"
            )

            self.stdout.write(self.style.SUCCESS(f"대시보드 URL: {dashboard_url}"))
            self.stdout.write(self.style.SUCCESS(f"퍼블릭 URL: {public_url}"))
            self.stdout.write(
                self.style.SUCCESS(
                    "이 URL은 로그인 없이 접근할 수 있으며 iframe에 임베드할 수 있습니다."
                )
            )

            # 결과 JSON 파일로 저장 (option)
            result_data = {
                "user_id": user_id,
                "folder_uid": folder_uid,
                "dashboard_uid": dashboard_uid,
                "dashboard_title": dashboard_title,
                "dashboard_url": dashboard_url,
                "public_url": public_url,
                "public_dashboard_uid": public_dashboard_result.get("uid"),
                "access_token": public_dashboard_result.get("accessToken"),
            }

            output_file = f"dashboard_{user_id}_{dashboard_uid}.json"
            with open(output_file, "w") as f:
                json.dump(result_data, f, indent=2)

            self.stdout.write(
                self.style.SUCCESS(f"결과가 {output_file} 파일에 저장되었습니다.")
            )
        else:
            self.stdout.write(self.style.ERROR("퍼블릭 대시보드 설정 실패!"))

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

        self.stdout.write(
            self.style.WARNING(f"태스크 {task_id} 시간 초과. 계속 진행합니다.")
        )
        return False

    def get_folder_uid_from_task(self, task_id):
        """태스크 결과에서 폴더 UID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and "uid" in result:
                    return result["uid"]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 추출 실패: {str(e)}"))
        return None

    def get_dashboard_uid_from_task(self, task_id):
        """태스크 결과에서 대시보드 UID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and "uid" in result:
                    return result["uid"]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"대시보드 UID 추출 실패: {str(e)}"))
        return None

    def get_public_dashboard_result_from_task(self, task_id):
        """태스크 결과에서 퍼블릭 대시보드 전체 결과 가져오기"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                return task.result
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"퍼블릭 대시보드 결과 추출 실패: {str(e)}")
            )
        return None

    def find_folder_uid_for_user(self, user_id):
        """사용자의 폴더 UID 검색"""
        try:
            # 최근 폴더 생성 태스크 조회
            recent_folder_task = (
                TaskResultModel.objects.filter(
                    task_name="create_grafana_folder",
                    result__contains=user_id,
                    status=TaskStatus.SUCCESS,
                )
                .order_by("-date_done")
                .first()
            )

            if recent_folder_task and recent_folder_task.result:
                result_data = recent_folder_task.result
                if isinstance(result_data, dict) and "uid" in result_data:
                    return result_data["uid"]

            # DB에서 찾지 못한 경우 그라파나 API 사용
            grafana_api = GrafanaAPI()
            folders = grafana_api.get_folders()

            # 폴더 이름 패턴
            folder_pattern = f"User_{user_id}_"

            for folder in folders:
                if folder_pattern in folder.get("title", ""):
                    return folder.get("uid")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 검색 실패: {str(e)}"))

        return None

    def slugify(self, text):
        """텍스트를 URL 슬러그로 변환"""
        import re

        from django.utils.text import slugify

        return slugify(text)
