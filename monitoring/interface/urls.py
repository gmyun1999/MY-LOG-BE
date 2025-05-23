from django.urls import path

from monitoring.interface.views.monitoring_provision_view import MonitoringProvisionView

urlpatterns = [
    path(
        "monitoring-projects/",
        view=MonitoringProvisionView.as_view(),
        name="monitoring-provision",
    ),
]

# monitoring_projects 에는 여러개의 dashboard가 포함될수있다.
# dashboard를 프로비저닝 하는것이 있음.
# 각 dashboard에는 해당 dashboard 전용 harvester 세팅이 있다.
