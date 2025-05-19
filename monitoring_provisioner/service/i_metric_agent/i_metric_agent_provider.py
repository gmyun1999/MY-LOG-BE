from abc import ABC


class IMetricAgentProvider(ABC):
    def create_agent_config(self):
        pass
    
    def create_logstash_config(self):
        pass