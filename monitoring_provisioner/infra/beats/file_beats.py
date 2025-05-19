from typing_extensions import override
from monitoring_provisioner.service.DTO.bootstrap_script_context import BootstrapScriptContext
from monitoring_provisioner.service.DTO.generated_config import GeneratedConfig
from monitoring_provisioner.infra.jinja2.jinja2_template_renderer import Jinja2TemplateRenderer
from monitoring_provisioner.service.DTO.log_collector_config_context import LogCollectorConfigContext
from monitoring_provisioner.service.i_log_agent.i_log_agent_provider import ILogAgentProvider
from monitoring_provisioner.service.i_template_renderer.template_renderer import ITemplateRenderer


class FileBeats(ILogAgentProvider):
    def __init__(self):
        # TODO : DI 적용
        self.template_provider: ITemplateRenderer = Jinja2TemplateRenderer()

    @override
    def create_log_collector_config(self, context: LogCollectorConfigContext) -> GeneratedConfig:
        """collector 설정을 render 해서 GeneratedConfig 로 반환"""
        return GeneratedConfig()
    
    @override
    def create_log_router_config(self, context: LogCollectorConfigContext) -> GeneratedConfig:
        """router 설정을 render 해서 GeneratedConfig 로 반환"""
        return GeneratedConfig()
    
    @override
    def create_bootstrap_script(self, context: BootstrapScriptContext) -> GeneratedConfig:
        """부트스트랩 스크립트를 render 해서 GeneratedConfig 로 반환"""
        return GeneratedConfig()