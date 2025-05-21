# monitoring_provisioner/infra/celery/tasks/base.py
import logging
import uuid

from celery import Task
from celery.exceptions import Ignore
from django.utils import timezone

from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel
from monitoring_provisioner.infra.redis.redis_client import redis_client

logger = logging.getLogger(__name__)

LOCK_EXPIRE = 10
PROC_EXPIRE = 60 * 60 * 24


class LockingTask(Task):
    abstract = True
    acks_late = True
    reject_on_worker_lost = True

    def __call__(self, *args, **kwargs):
        task_result_id = args[0]
        print(f"task_result_id!!!!!!!!!!!!!!!!!!!!!!!!: {task_result_id}")
        lock_key = f"lock:dashboard:{task_result_id}"
        proc_key = f"done:dashboard:{task_result_id}"
        token = str(uuid.uuid4())

        logger.info(f"태스크 실행 시작: {self.name}, ID: {task_result_id}")

        if redis_client.exists(proc_key):
            logger.info(f"이미 처리된 태스크: {task_result_id}")
            if hasattr(self.request, "acknowledge"):
                self.request.acknowledge()
            raise Ignore(f"{task_result_id} already processed")

        if not redis_client.set(lock_key, token, nx=True, ex=LOCK_EXPIRE):
            logger.info(f"이미 실행 중인 태스크: {task_result_id}")
            if hasattr(self.request, "acknowledge"):
                self.request.acknowledge()
            raise Ignore(f"Task {task_result_id} is already running")

        try:
            logger.info(f"태스크 {task_result_id} 실행 중...")

            # 태스크 결과 정보 로그
            try:
                task_result = TaskResultModel.objects.get(id=task_result_id)
                logger.info(
                    f"태스크 정보: {task_result.task_name}, 상태: {task_result.status}"
                )
            except Exception as e:
                logger.error(f"태스크 정보 조회 실패: {e}")

            result = self.run(*args, **kwargs)
            logger.info(f"태스크 {task_result_id} 성공적으로 완료: {result}")

            # 성공 시 retries 카운트도 함께 저장
            redis_client.set(proc_key, "1", ex=PROC_EXPIRE)
            TaskResultModel.objects.filter(id=task_result_id).update(
                status=TaskStatus.SUCCESS,
                result=result,
                retries=self.request.retries,
                date_done=timezone.now(),
            )
            return result

        except Ignore:
            logger.info(f"태스크 {task_result_id} 무시됨")
            raise

        except Exception as exc:
            logger.error(f"태스크 {task_result_id} 실행 중 오류: {exc}", exc_info=True)
            raise self.retry(exc=exc)

        finally:
            try:
                if redis_client.get(lock_key) == token:
                    redis_client.delete(lock_key)
                    logger.info(f"태스크 {task_result_id} 락 해제")
            except Exception as cleanup_exc:
                logger.error(f"락 해제 중 오류: {cleanup_exc}")
                raise self.retry(exc=cleanup_exc)
