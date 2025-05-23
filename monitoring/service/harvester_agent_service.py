import time

from monitoring.domain.log_agent.agent_provision_context import (
    AgentProvisioningContext,
    PlatformType,
)
from monitoring.domain.log_agent.log_collector import LogCollectorConfigContext
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.domain.log_agent.rendered_config import RenderedConfigFile
from monitoring.infra.beats.file_beats import FileBeats
from monitoring.infra.s3.s3_agent_storage import S3AgentStorageProvider
from monitoring.service.i_log_agent.i_log_agent_provider import ILogAgentProvider
from monitoring.service.i_storage.i_storage_provider import IAgentStorageProvider


class HarvesterAgentService:
    def __init__(self):
        # TODO: DI 적용 예정
        self.log_agent_provider: ILogAgentProvider = FileBeats()
        self.storage_provider: IAgentStorageProvider = S3AgentStorageProvider()

    def create_log_agent_config(
        self,
        collector_context: LogCollectorConfigContext,
        router_context: LogRouterConfigContext,
    ) -> tuple[RenderedConfigFile, RenderedConfigFile]:
        """
        collector.yml 과 router.yml 렌더링

        :param context: 로그 에이전트 설정용 DTO
        :return: (collector_config, router_config)
        """
        collector = self.log_agent_provider.create_log_collector_config(
            collector_context
        )
        router = self.log_agent_provider.create_log_router_config(router_context)
        return collector, router

    def create_agent_set_up_script(
        self, context: AgentProvisioningContext
    ) -> RenderedConfigFile:
        """
        bootstrap 스크립트 렌더링

        :param context: 부트스트랩 스크립트용 DTO
        :return: GeneratedConfig (filename + content)
        """
        return self.log_agent_provider.create_agent_set_up_script(context)

    def _upload_generated(
        self, resource_id: str, gen: RenderedConfigFile, ts: int
    ) -> str:
        key = self.storage_provider.get_object_key(resource_id, ts, gen.filename)

        ext = gen.filename.rsplit(".", 1)[-1].lower()
        if ext in ("yml", "yaml"):
            content_type = "text/yaml"
        elif ext == "sh":
            content_type = "text/x-shellscript"
        else:
            content_type = "application/octet-stream"

        return self.storage_provider.upload(
            data=gen.content, key=key, content_type=content_type
        )

    def download_log_agent_set_up_script(
        self,
        resource_id: str,
        log_collector_ctx: LogCollectorConfigContext,
        log_router_ctx: LogRouterConfigContext,
        platform: PlatformType,
    ) -> AgentProvisioningContext:
        """
        1) collector/router config 생성
        2) bootstrap 스크립트 생성
        3) 모두 S3에 업로드
        4) AgentProvisioningContext 반환

        :param resource_id: 프로젝트 식별자
        :param log_ctx: 로그 에이전트 설정 컨텍스트
        :param boot_ctx: bootstrap 스크립트 컨텍스트

        """
        ts = int(time.time())

        # 템플릿 렌더링
        collector_cfg, router_cfg = self.create_log_agent_config(
            log_collector_ctx, log_router_ctx
        )

        collector_key = self.storage_provider.get_object_key(
            resource_id, ts, collector_cfg.filename
        )
        router_key = self.storage_provider.get_object_key(
            resource_id, ts, router_cfg.filename
        )

        collector_url = self.storage_provider.get_object_url(collector_key)
        router_url = self.storage_provider.get_object_url(router_key)

        agent_base_url = self.storage_provider.get_base_static_url()
        bootstrap_ctx = AgentProvisioningContext(
            base_static_url=agent_base_url,
            collector_config_url=collector_url,
            router_config_url=router_url,
            timestamp=ts,
            platform=platform,
        )
        bootstrap_cfg = self.create_agent_set_up_script(bootstrap_ctx)

        collector_upload_url = self._upload_generated(resource_id, collector_cfg, ts)
        router_upload_url = self._upload_generated(resource_id, router_cfg, ts)
        bootstrap_upload_url = self._upload_generated(resource_id, bootstrap_cfg, ts)

        return AgentProvisioningContext(
            base_static_url=agent_base_url,
            collector_config_url=collector_upload_url,
            router_config_url=router_upload_url,
            set_up_script_url=bootstrap_upload_url,
            timestamp=ts,
            platform=platform,
        )
