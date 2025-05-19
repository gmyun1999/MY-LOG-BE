from django.urls import path

from monitoring_provisioner.interface.views.monitoring_provision_view import MonitoringProvisionView


urlpatterns = [
    path("monitoring-projects/", view=MonitoringProvisionView.as_view(), name="monitoring-provision"),
    path("monitoring-projects/dashboards/", view=MonitoringProvisionView.as_view(), name="monitoring-dashboards"),
]