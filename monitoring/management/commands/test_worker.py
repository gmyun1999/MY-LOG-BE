import time

from django.core.management.base import BaseCommand

from monitoring.domain.task_result import TaskStatus
from monitoring.infra.celery.task_executor.grafana_executor import GrafanaTaskExecutor
from monitoring.infra.grafana.grafana_api import GrafanaAPI
from monitoring.infra.models.task_result_model import TaskResultModel


class Command(BaseCommand):
    help = "Test Grafana integration with Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=str, default="test_user_123")
        parser.add_argument("--user-name", type=str, default="Test User")
        parser.add_argument("--dashboard-title", type=str, default="Test Dashboard")
        parser.add_argument(
            "--action",
            type=str,
            choices=[
                "folder",
                "account",
                "token",
                "dashboard",
                "permissions",
                "public",
                "all",
                "sequence",
            ],
            default="all",
        )
        parser.add_argument(
            "--wait-for-completion",
            action="store_true",
            help="Wait for tasks to complete before proceeding",
        )

    def handle(self, *args, **options):
        executor = GrafanaTaskExecutor()
        user_id = options["user_id"]
        user_name = options["user_name"]
        dashboard_title = options["dashboard_title"]
        action = options["action"]
        wait_for_completion = options["wait_for_completion"]

        self.stdout.write(self.style.SUCCESS(f"테스트 시작: {action} 작업"))

        task_ids = {}

        # 순차적 실행 옵션
        if action == "sequence":
            self.stdout.write(
                "폴더 생성 → 서비스 계정 → 서비스 토큰 → 권한 설정 → 대시보드 → 퍼블릭 대시보드 순차 실행 중..."
            )

            # 1. 폴더 생성
            self.stdout.write("1. 폴더 생성 요청 중...")
            folder_task_id = executor.dispatch_create_user_folder(user_id, user_name)
            self.stdout.write(
                self.style.SUCCESS(
                    f"폴더 생성 태스크 등록 완료. Task ID: {folder_task_id}"
                )
            )

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
            self.stdout.write(
                self.style.SUCCESS(
                    f"서비스 계정 생성 태스크 등록 완료. Task ID: {account_task_id}"
                )
            )

            if wait_for_completion:
                self.wait_for_task_completion(account_task_id)
                service_account_id = self.get_service_account_id_from_task(
                    account_task_id
                )
            else:
                # 서비스 계정 생성에 시간이 필요하므로 잠시 대기
                time.sleep(2)
                service_account_id = self.get_service_account_id_from_task(
                    account_task_id
                )

            # 3. 서비스 토큰 생성
            service_token = None
            if service_account_id:
                self.stdout.write(
                    f"3. 서비스 토큰 생성 요청 중... (서비스 계정 ID: {service_account_id})"
                )
                token_task_id = executor.create_service_token(
                    service_account_id, user_id
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"서비스 토큰 생성 태스크 등록 완료. Task ID: {token_task_id}"
                    )
                )

                if wait_for_completion:
                    self.wait_for_task_completion(token_task_id)
                    service_token = self.get_service_token_from_task(token_task_id)
                else:
                    # 토큰 생성에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                    service_token = self.get_service_token_from_task(token_task_id)

                # 태스크 ID 정보 추가
                task_ids["token"] = token_task_id
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "서비스 계정 ID를 가져올 수 없어 토큰 생성을 진행하지 않습니다."
                    )
                )

            # 4. 폴더 권한 설정
            if folder_uid and service_account_id:
                self.stdout.write(
                    f"4. 폴더 권한 설정 요청 중... (폴더 UID: {folder_uid}, 서비스 계정 ID: {service_account_id})"
                )
                permission_task_id = executor.set_folder_permissions(
                    folder_uid, service_account_id
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"폴더 권한 설정 태스크 등록 완료. Task ID: {permission_task_id}"
                    )
                )

                if wait_for_completion:
                    self.wait_for_task_completion(permission_task_id)
                else:
                    # 권한 설정에 시간이 필요하므로 잠시 대기
                    time.sleep(2)

                # 태스크 ID 정보 추가
                task_ids["permission"] = permission_task_id
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "폴더 UID 또는 서비스 계정 ID를 가져올 수 없어 권한 설정을 진행하지 않습니다."
                    )
                )

            # 5. 대시보드 생성
            dashboard_uid = None
            if folder_uid:
                self.stdout.write(
                    f"5. 대시보드 생성 요청 중... (폴더 UID: {folder_uid})"
                )
                dashboard_task_id = executor.create_dashboard(
                    user_id=user_id,
                    title=dashboard_title,
                    panels=[
                        {
                            "id": 1,
                            "type": "graph",
                            "title": "CPU Usage",
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                        }
                    ],
                    folder_uid=folder_uid,  # 폴더 UID 명시적 전달
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"대시보드 생성 태스크 등록 완료. Task ID: {dashboard_task_id}"
                    )
                )

                if wait_for_completion:
                    self.wait_for_task_completion(dashboard_task_id)
                    dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)
                else:
                    # 대시보드 생성에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                    dashboard_uid = self.get_dashboard_uid_from_task(dashboard_task_id)

                # 대시보드 정보 추가
                task_ids["dashboard"] = dashboard_task_id
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "폴더 UID를 가져올 수 없어 대시보드를 생성하지 않습니다."
                    )
                )

            # 6. 대시보드 공유 URL 생성 (퍼블릭 대시보드 생성 추가)
            public_dashboard_uid = None
            if dashboard_uid:
                self.stdout.write("6. 퍼블릭 대시보드 생성 요청 중...")
                public_dashboard_task_id = executor.dispatch_create_public_dashboard(
                    dashboard_uid
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"퍼블릭 대시보드 생성 태스크 등록 완료. Task ID: {public_dashboard_task_id}"
                    )
                )

                if wait_for_completion:
                    self.wait_for_task_completion(public_dashboard_task_id)
                    public_dashboard_uid = self.get_public_dashboard_uid_from_task(
                        public_dashboard_task_id
                    )
                else:
                    # 대시보드 생성에 시간이 필요하므로 잠시 대기
                    time.sleep(2)
                    public_dashboard_uid = self.get_public_dashboard_uid_from_task(
                        public_dashboard_task_id
                    )

                # 태스크 ID 정보 추가
                task_ids["public_dashboard"] = public_dashboard_task_id

                # URL 생성
                grafana_api = GrafanaAPI()
                # base_url에서 마지막 슬래시 제거
                base_url = grafana_api.base_url.rstrip("/")

                # 출력할 URL 생성
                urls = []

                # 1. 기본 대시보드 URL
                embed_url = f"{base_url}/d/{dashboard_uid}/test-dashboard?orgId=1&kiosk&theme=light"
                urls.append(("기본 대시보드 URL", embed_url))

                # 2. 서비스 계정 토큰 API URL
                if service_token:
                    auth_url = f"{base_url}/api/dashboards/uid/{dashboard_uid}"
                    urls.append(
                        ("API 접근 토큰 헤더", f"Authorization: Bearer {service_token}")
                    )
                    urls.append(("API 요청 URL", auth_url))

                # 3. 퍼블릭 대시보드 URL
                if public_dashboard_uid:
                    # 퍼블릭 대시보드 결과 가져오기
                    public_dashboard_result = (
                        self.get_public_dashboard_result_from_task(
                            public_dashboard_task_id
                        )
                    )

                    if (
                        public_dashboard_result
                        and "accessToken" in public_dashboard_result
                    ):
                        # accessToken 사용
                        public_url = f"{base_url}/public-dashboards/{public_dashboard_result['accessToken']}"
                        urls.append(("퍼블릭 대시보드 URL (로그인 불필요)", public_url))
                    else:
                        # 기존 uid 방식 사용
                        public_url = (
                            f"{base_url}/public-dashboards/{public_dashboard_uid}"
                        )
                        urls.append(("퍼블릭 대시보드 URL (로그인 불필요)", public_url))

                # 결과 출력
                self.stdout.write("")
                self.stdout.write(
                    self.style.SUCCESS("대시보드가 성공적으로 생성되었습니다!")
                )
                self.stdout.write(self.style.SUCCESS(f"대시보드 UID: {dashboard_uid}"))
                if service_account_id:
                    self.stdout.write(
                        self.style.SUCCESS(f"서비스 계정 ID: {service_account_id}")
                    )
                if service_token:
                    self.stdout.write(
                        self.style.SUCCESS(f"서비스 토큰: {service_token}")
                    )
                if public_dashboard_uid:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"퍼블릭 대시보드 UID: {public_dashboard_uid}"
                        )
                    )

                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("대시보드 접근을 위한 정보:"))

                for i, (title, url) in enumerate(urls, 1):
                    self.stdout.write(self.style.SUCCESS(f"{i}. {title}:"))
                    self.stdout.write(self.style.SUCCESS(url))
                    self.stdout.write("")

            # 태스크 ID 정보 추가
            task_ids["folder"] = folder_task_id
            task_ids["account"] = account_task_id

        elif action in ["folder", "all"]:
            self.stdout.write("폴더 생성 요청 중...")
            task_id = executor.dispatch_create_user_folder(user_id, user_name)
            task_ids["folder"] = task_id
            self.stdout.write(
                self.style.SUCCESS(f"폴더 생성 태스크 등록 완료. Task ID: {task_id}")
            )

        elif action in ["account", "all"]:
            self.stdout.write("서비스 계정 생성 요청 중...")
            task_id = executor.create_service_account(user_id, "Viewer")
            task_ids["account"] = task_id
            self.stdout.write(
                self.style.SUCCESS(
                    f"서비스 계정 생성 태스크 등록 완료. Task ID: {task_id}"
                )
            )

        elif action in ["token"]:
            self.stdout.write("서비스 토큰 생성 요청 중...")
            # 서비스 계정 ID 찾기
            account_name = f"service-{user_id}"
            service_account_id = self.find_service_account_id(account_name)
            if not service_account_id:
                self.stdout.write(
                    self.style.ERROR(f"서비스 계정 {account_name}을 찾을 수 없습니다.")
                )
                return

            self.stdout.write(f"서비스 계정 ID: {service_account_id}")
            task_id = executor.create_service_token(service_account_id, user_id)
            task_ids["token"] = task_id
            self.stdout.write(
                self.style.SUCCESS(
                    f"서비스 토큰 생성 태스크 등록 완료. Task ID: {task_id}"
                )
            )

            if wait_for_completion:
                self.wait_for_task_completion(task_id)
                token = self.get_service_token_from_task(task_id)
                if token:
                    self.stdout.write(
                        self.style.SUCCESS(f"생성된 서비스 토큰: {token}")
                    )

        elif action in ["permissions"]:
            self.stdout.write("폴더 권한 설정 요청 중...")
            # 폴더 UID 찾기
            folder_uid = self.find_folder_uid_for_user(user_id)
            if not folder_uid:
                self.stdout.write(
                    self.style.ERROR(f"사용자 {user_id}의 폴더를 찾을 수 없습니다.")
                )
                return

            # 서비스 계정 ID 찾기
            account_name = f"service-{user_id}"
            service_account_id = self.find_service_account_id(account_name)
            if not service_account_id:
                self.stdout.write(
                    self.style.ERROR(f"서비스 계정 {account_name}을 찾을 수 없습니다.")
                )
                return

            self.stdout.write(
                f"폴더 UID: {folder_uid}, 서비스 계정 ID: {service_account_id}"
            )
            task_id = executor.set_folder_permissions(folder_uid, service_account_id)
            task_ids["permissions"] = task_id
            self.stdout.write(
                self.style.SUCCESS(
                    f"폴더 권한 설정 태스크 등록 완료. Task ID: {task_id}"
                )
            )

        elif action in ["public"]:
            self.stdout.write("퍼블릭 대시보드 생성 요청 중...")
            # 대시보드 UID 찾기
            dashboard_uid = self.find_dashboard_uid_for_user(user_id)
            if not dashboard_uid:
                self.stdout.write(
                    self.style.ERROR(f"사용자 {user_id}의 대시보드를 찾을 수 없습니다.")
                )
                return

            self.stdout.write(f"대시보드 UID: {dashboard_uid}")
            task_id = executor.dispatch_create_public_dashboard(dashboard_uid)
            task_ids["public"] = task_id
            self.stdout.write(
                self.style.SUCCESS(
                    f"퍼블릭 대시보드 생성 태스크 등록 완료. Task ID: {task_id}"
                )
            )

            if wait_for_completion:
                self.wait_for_task_completion(task_id)
                public_uid = self.get_public_dashboard_uid_from_task(task_id)
                if public_uid:
                    grafana_api = GrafanaAPI()
                    public_url = f"{grafana_api.base_url.rstrip('/')}/public-dashboards/{public_uid}"
                    self.stdout.write(
                        self.style.SUCCESS(f"퍼블릭 대시보드 URL: {public_url}")
                    )

        elif action in ["dashboard", "all"]:
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
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
                    }
                ],
                folder_uid=folder_uid,  # 발견된 경우 전달
            )
            task_ids["dashboard"] = task_id
            self.stdout.write(
                self.style.SUCCESS(
                    f"대시보드 생성 태스크 등록 완료. Task ID: {task_id}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"테스트 완료. 등록된 태스크 ID: {task_ids}")
        )

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

    def get_service_account_id_from_task(self, task_id):
        """태스크 결과에서 서비스 계정 ID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and "id" in result:
                    return result["id"]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 계정 ID 추출 실패: {str(e)}"))
        return None

    def get_service_token_from_task(self, task_id):
        """태스크 결과에서 서비스 토큰 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and "key" in result:
                    return result["key"]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 토큰 추출 실패: {str(e)}"))
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

    def get_public_dashboard_uid_from_task(self, task_id):
        """태스크 결과에서 퍼블릭 대시보드 UID 추출"""
        try:
            task = TaskResultModel.objects.get(id=task_id)
            if task.status == TaskStatus.SUCCESS and task.result:
                result = task.result
                if isinstance(result, dict) and "uid" in result:
                    return result["uid"]
                # 다른 형식의 응답 처리
                if (
                    isinstance(result, dict)
                    and "publicDashboard" in result
                    and "uid" in result["publicDashboard"]
                ):
                    return result["publicDashboard"]["uid"]
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"퍼블릭 대시보드 UID 추출 실패: {str(e)}")
            )
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
            from monitoring.infra.grafana.grafana_api import GrafanaAPI

            api = GrafanaAPI()
            folders = api.get_folders()

            # 폴더 이름 패턴
            folder_pattern = f"User_{user_id}_"

            for folder in folders:
                if folder_pattern in folder.get("title", ""):
                    return folder.get("uid")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"폴더 UID 검색 실패: {str(e)}"))

        return None

    def find_service_account_id(self, account_name):
        """서비스 계정 ID 검색"""
        try:
            # 최근 서비스 계정 생성 태스크 조회
            recent_account_task = (
                TaskResultModel.objects.filter(
                    task_name="create_grafana_service_account",
                    result__contains=account_name,
                    status=TaskStatus.SUCCESS,
                )
                .order_by("-date_done")
                .first()
            )

            if recent_account_task and recent_account_task.result:
                result_data = recent_account_task.result
                if isinstance(result_data, dict) and "id" in result_data:
                    return result_data["id"]

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"서비스 계정 ID 검색 실패: {str(e)}"))

        return None

    def find_dashboard_uid_for_user(self, user_id):
        """사용자의 대시보드 UID 검색"""
        try:
            # 최근 대시보드 생성 태스크 조회
            recent_dashboard_task = (
                TaskResultModel.objects.filter(
                    task_name="create_grafana_dashboard",
                    result__contains=user_id,
                    status=TaskStatus.SUCCESS,
                )
                .order_by("-date_done")
                .first()
            )

            if recent_dashboard_task and recent_dashboard_task.result:
                result_data = recent_dashboard_task.result
                if isinstance(result_data, dict) and "uid" in result_data:
                    return result_data["uid"]

            # DB에서 찾지 못한 경우 그라파나 API 사용
            from monitoring.infra.grafana.grafana_api import GrafanaAPI

            api = GrafanaAPI()
            # 대시보드 검색 로직 (API 제공 시)
            # 현재 API에서는 대시보드 목록을 가져오는 기능이 구현되어 있지 않음

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"대시보드 UID 검색 실패: {str(e)}"))

        return None
