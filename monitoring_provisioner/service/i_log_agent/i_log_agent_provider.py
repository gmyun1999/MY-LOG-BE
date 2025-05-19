from abc import ABC, abstractmethod

from monitoring_provisioner.service.DTO.bootstrap_script_context import BootstrapScriptContext
from monitoring_provisioner.service.DTO.generated_config import GeneratedConfig
from monitoring_provisioner.service.DTO.log_collector_config_context import LogCollectorConfigContext


class ILogAgentProvider(ABC):

    @abstractmethod
    def create_log_collector_config(self, context: LogCollectorConfigContext) -> GeneratedConfig:
        """collector 설정을 render 해서 GeneratedConfig 로 반환"""

    @abstractmethod
    def create_log_router_config(self, context: LogCollectorConfigContext) -> GeneratedConfig:
        """router 설정을 render 해서 GeneratedConfig 로 반환"""

    @abstractmethod
    def create_bootstrap_script(self, context: BootstrapScriptContext) -> GeneratedConfig:
        """부트스트랩 스크립트를 render 해서 GeneratedConfig 로 반환"""