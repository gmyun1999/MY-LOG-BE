
from monitoring_provisioner.infra.celery.tasks.utils import locking_task

@locking_task(max_retries=3, default_retry_delay=2)
def send_dashboard_creation_request(self, task_result_id: str):
    # 여기 순수 Grafana 호출 로직만!
    # return grafana_api.create_dashboard(task_result_id)
    # return "성공했음"
    # raise NotImplementedError("테스트용에러임")
    if self.request.retries == 0:
        raise NotImplementedError("테스트용에러임")
    # 두 번째 실행부터는 정상 반환
    return "성공했음"