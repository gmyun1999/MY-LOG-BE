from datetime import datetime

from django.core.management.base import BaseCommand

from monitoring.domain.log_agent.agent_provision_context import PlatformType
from monitoring.domain.log_agent.log_collector import (
    FilterCondition,
    FilterOperator,
    LogCollectorConfigContext,
    LogInputType,
)
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.service.harvester_agent_service import HarvesterAgentService


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 예시 resource_id
        resource_id = "test-project-id"

        # 예시 컨텍스트 구성
        collector_ctx = LogCollectorConfigContext(
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

        router_context = LogRouterConfigContext(
            project_id="proj2",
            beats_port=5044,
            mq_host="127.0.0.1",
            mq_port=5672,
            mq_user="guest",
            mq_password="guest",
            mq_vhost="/",
            mq_exchange="app_logs_exchange",
            mq_exchange_type="direct",
            mq_routing_key="logs_1",
            mq_persistent=True,
            mq_heartbeat=30,
        )

        platform = PlatformType.WINDOWS  # 예시값

        # 서비스 호출
        svc = HarvesterAgentService()
        urls = svc.download_log_agent_set_up_script(
            resource_id=resource_id,
            log_collector_ctx=collector_ctx,
            log_router_ctx=router_context,
            platform=platform,
        )

        # 결과 출력
        self.stdout.write(self.style.SUCCESS("✔ 에이전트 구성 완료"))
        for name, url in urls.items():
            self.stdout.write(f"{name}: {url}")
