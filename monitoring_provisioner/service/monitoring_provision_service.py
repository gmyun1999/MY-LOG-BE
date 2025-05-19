import time
from monitoring_provisioner.service.DTO.bootstrap_script_context import BootstrapScriptContext
from monitoring_provisioner.service.DTO.generated_config import GeneratedConfig
from monitoring_provisioner.infra.beats.file_beats import FileBeats
from monitoring_provisioner.infra.beats.metric_beats import MetricBeats
from monitoring_provisioner.infra.s3.s3 import S3StorageProvider
from monitoring_provisioner.service.DTO.log_collector_config_context import LogCollectorConfigContext
from monitoring_provisioner.service.i_log_agent.i_log_agent_provider import ILogAgentProvider
from monitoring_provisioner.service.i_storage.i_storage_provider import IStorageProvider

class MonitoringProvisionService:
    def __init__(self):
        # TODO: DI 적용 예정
        self.log_agent_provider: ILogAgentProvider = FileBeats()
        self.storage_provider: IStorageProvider    = S3StorageProvider()

    def create_log_agent_config(
        self,
        context: LogCollectorConfigContext
    ) -> tuple[GeneratedConfig, GeneratedConfig]:
        """
        collector.yml 과 router.yml 렌더링

        :param context: 로그 에이전트 설정용 DTO
        :return: (collector_config, router_config)
        """
        collector = self.log_agent_provider.create_log_collector_config(context)
        router    = self.log_agent_provider.create_log_router_config(context)
        return collector, router

    def create_bootstrap_script(
        self,
        context: BootstrapScriptContext
    ) -> GeneratedConfig:
        """
        bootstrap 스크립트 렌더링

        :param context: 부트스트랩 스크립트용 DTO
        :return: GeneratedConfig (filename + content)
        """
        return self.log_agent_provider.create_bootstrap_script(context)

    def _upload_generated(
        self,
        resource_id: str,
        gen: GeneratedConfig,
        ts: int
    ) -> str:
        """
        GeneratedConfig를 S3에 업로드하고, public URL 반환

        :param resource_id: 프로젝트 식별자
        :param gen: 렌더링된 파일 (filename, content)
        :param ts: 타임스탬프 (유니크 경로용)
        :return: 업로드된 객체의 public URL
        """
        key = f"configs/{resource_id}/{ts}/{gen.filename}"

        ext = gen.filename.rsplit('.', 1)[-1].lower()
        if ext in ('yml', 'yaml'):
            content_type = 'text/yaml'
        elif ext == 'sh':
            content_type = 'text/x-shellscript'
        else:
            content_type = 'application/octet-stream'

        return self.storage_provider.upload(
            data=gen.content,
            key=key,
            content_type=content_type
        )

    def provision_monitoring_project(
        self,
        resource_id: str,
        log_ctx: LogCollectorConfigContext,
        boot_ctx: BootstrapScriptContext
    ) -> dict[str, str]:
        """
        1) collector/router config 생성
        2) bootstrap 스크립트 생성
        3) 모두 S3에 업로드
        4) URL 반환

        :param resource_id: 프로젝트 식별자
        :param log_ctx: 로그 에이전트 설정 컨텍스트
        :param boot_ctx: bootstrap 스크립트 컨텍스트
        :return: {
            'collector_config_url': ...,
            'router_config_url': ...,
            'bootstrap_script_url': ...
        }
        """
        # 1) 템플릿 렌더링
        collector_cfg, router_cfg = self.create_log_agent_config(log_ctx)
        bootstrap_cfg             = self.create_bootstrap_script(boot_ctx)

        # 2) 필요한 granfana worker에게 넘기기 (비동기)
        # TODO : granfana worker에게 넘기기
        
        # 3) S3 업로드
        ts = int(time.time())
        return {
            'collector_config_url': self._upload_generated(resource_id, collector_cfg, ts),
            'router_config_url':    self._upload_generated(resource_id, router_cfg,    ts),
            'bootstrap_script_url': self._upload_generated(resource_id, bootstrap_cfg, ts),
        }
        