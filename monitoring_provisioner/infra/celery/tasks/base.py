import uuid
from celery import Task
from celery.exceptions import Ignore
from django.utils import timezone
from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
from monitoring_provisioner.infra.redis.redis_client import redis_client

LOCK_EXPIRE = 10
PROC_EXPIRE = 60 * 60 * 24

class LockingTask(Task):
    abstract = True
    acks_late = True
    reject_on_worker_lost = True

    def __call__(self, *args, **kwargs):
        task_result_id = args[0]
        lock_key = f"lock:dashboard:{task_result_id}"
        proc_key = f"done:dashboard:{task_result_id}"
        token = str(uuid.uuid4())

        if redis_client.exists(proc_key):
            if hasattr(self.request, "acknowledge"):
                self.request.acknowledge()
            raise Ignore(f"{task_result_id} already processed")

        if not redis_client.set(lock_key, token, nx=True, ex=LOCK_EXPIRE):
            if hasattr(self.request, "acknowledge"):
                self.request.acknowledge()
            raise Ignore(f"Task {task_result_id} is already running")

        try:
            result = self.run(*args, **kwargs)

            # 성공 시 retries 카운트도 함께 저장
            redis_client.set(proc_key, "1", ex=PROC_EXPIRE)
            TaskResultModel.objects.filter(id=task_result_id).update(
                status=TaskStatus.SUCCESS,
                result=result,
                retries=self.request.retries,
                date_done=timezone.now()
            )
            return result

        except Ignore:
            raise
        
        except Exception as exc:
            raise self.retry(exc=exc)

        finally:
            try:
                if redis_client.get(lock_key) == token:
                    redis_client.delete(lock_key)
            except Exception as cleanup_exc:
                raise self.retry(exc=cleanup_exc)
