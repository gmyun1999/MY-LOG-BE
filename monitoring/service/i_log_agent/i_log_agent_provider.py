from abc import ABC, abstractmethod

from monitoring.domain.log_agent.agent_provision_context import AgentProvisioningContext
from monitoring.domain.log_agent.log_collector import LogCollectorConfigContext
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.domain.log_agent.rendered_config import RenderedConfigFile


class ILogAgentProvider(ABC):

    @abstractmethod
    def create_log_collector_config(
        self, context: LogCollectorConfigContext
    ) -> RenderedConfigFile:
        """collector 설정을 render 해서 GeneratedConfig 로 반환"""
        ...

    @abstractmethod
    def create_log_router_config(
        self, context: LogRouterConfigContext
    ) -> RenderedConfigFile:
        """router 설정을 render 해서 GeneratedConfig 로 반환"""
        ...

    @abstractmethod
    def create_agent_set_up_script(
        self, context: AgentProvisioningContext
    ) -> RenderedConfigFile:
        """부트스트랩 스크립트를 render 해서 GeneratedConfig 로 반환"""
        ...
