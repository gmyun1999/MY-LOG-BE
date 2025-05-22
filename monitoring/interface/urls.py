from django.urls import path

from monitoring.interface.views.monitoring_provision_view import MonitoringProvisionView

urlpatterns = [
    path(
        "monitoring-projects/",
        view=MonitoringProvisionView.as_view(),
        name="monitoring-provision",
    ),
]
