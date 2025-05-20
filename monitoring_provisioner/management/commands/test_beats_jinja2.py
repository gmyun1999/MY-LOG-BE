# monitoring_provisioner/management/commands/test_filebeats.py

import os

from django.core.management.base import BaseCommand

from monitoring_provisioner.domain.log_agent.log_collector import (
    FilterCondition,
    FilterOperator,
    JsonFieldMapping,
    LogCollectorConfigContext,
    LogInputType,
)
from monitoring_provisioner.infra.beats.file_beats import FileBeats

OUTPUT_DIR = os.path.join(os.getcwd(), "collector_output")


class Command(BaseCommand):
    help = "create_log_collector_config()만 테스트해서 파일로 저장"

    def handle(self, *args, **options):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        provider = FileBeats()

        # PLAIN 타입
        plain_ctx = LogCollectorConfigContext(
            project_id="proj1",
            hosts=["127.0.0.1:5044"],
            log_paths=["/var/log/app.log"],
            input_type=LogInputType.PLAIN,
            multiline_pattern=r"^(INFO|WARN|ERROR)",
            custom_plain_fields=[
                "level",
                "<timestamp>",
                "|",
                "module",
                "||",
                "[msg_detail]",
            ],
            filters=[
                FilterCondition(
                    field="level", operator=FilterOperator.EQUALS, value="ERROR"
                ),
                FilterCondition(
                    field="level", operator=FilterOperator.EQUALS, value="WARN"
                ),
            ],
        )
        plain_file = provider.create_log_collector_config(plain_ctx)
        with open(os.path.join(OUTPUT_DIR, plain_file.filename), "wb") as f:
            f.write(plain_file.content)
        self.stdout.write(f"생성됨: {plain_file.filename}")

        # JSON 타입
        json_ctx = LogCollectorConfigContext(
            project_id="proj2",
            hosts=["127.0.0.1:5044"],
            log_paths=["/var/log/app.json"],
            input_type=LogInputType.JSON,
            # 필수 필드
            timestamp_field="@timestamp",
            timestamp_json_path="app.meta.time",  # ← 실제 JSON 내부 경로 예시로 추가
            log_level="log_level",  # ← 사용자가 지정한 최종 필드명
            log_level_json_path="app.meta.level",  # ← JSON 내 실제 경로
            # 사용자 정의 필드 복사
            custom_json_fields=[
                JsonFieldMapping(name="user", json_path="user.name"),
                JsonFieldMapping(name="age", json_path="user.age"),
                JsonFieldMapping(name="weight", json_path="user.weight"),
            ],
            # 조건 필터
            filters=[
                FilterCondition(
                    field="user.age", operator=FilterOperator.NOT_EQUALS, value="30"
                )
            ],
        )

        json_file = provider.create_log_collector_config(json_ctx)
        with open(os.path.join(OUTPUT_DIR, json_file.filename), "wb") as f:
            f.write(json_file.content)
        self.stdout.write(f"생성됨: {json_file.filename}")

        self.stdout.write(f"\n→ `{OUTPUT_DIR}` 폴더에서 결과 확인")
