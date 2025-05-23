from django.urls import path

from monitoring.interface.views.log_monitoring_project_views import (
    LogMonitoringProjectStep1View,
    LogMonitoringProjectStep2View,
)

urlpatterns = [
    path(
        "monitoring/log-project/step1",
        LogMonitoringProjectStep1View.as_view(),
        name="logProjectStep1",
    ),
    path(
        "monitoring/log-project/step2",
        LogMonitoringProjectStep2View.as_view(),
        name="logProjectStep2",
    ),
]
