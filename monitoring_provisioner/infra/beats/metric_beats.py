from typing import override
from monitoring_provisioner.service.i_metric_agent.i_metric_agent_provider import IMetricAgentProvider


class MetricBeats(IMetricAgentProvider):
    def __init__(self, config):
        self.config = config

    @override
    def create_agent_config(self):
        pass