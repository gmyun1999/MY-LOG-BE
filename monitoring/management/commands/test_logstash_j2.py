import os
from datetime import datetime

from django.core.management.base import BaseCommand

from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.infra.beats.file_beats import FileBeats

OUTPUT_DIR = os.path.join(os.getcwd(), "router_output")


class Command(BaseCommand):
    help = "create_log_router_config() 테스트용 설정파일 생성"

    def handle(self, *args, **options):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        provider = FileBeats()

        context = LogRouterConfigContext(
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

        config_file = provider.create_log_router_config(context)

        path = os.path.join(OUTPUT_DIR, config_file.filename)
        with open(path, "wb") as f:
            f.write(config_file.content)

        self.stdout.write(f"라우터 설정 생성됨: {config_file.filename}")
        self.stdout.write(f"\n→ `{OUTPUT_DIR}` 폴더에서 결과 확인")
