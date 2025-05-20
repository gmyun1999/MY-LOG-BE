from django.core.management.base import BaseCommand
from celery import shared_task
from config.celery import app

# 공유 태스크로 등록
@shared_task(name='test_celery_task')
def test_task():
    print("이 메시지는 Celery 워커에서 출력됩니다!")
    return "테스트 태스크 완료!"

class Command(BaseCommand):
    help = "테스트 Celery 태스크 실행"

    def handle(self, *args, **kwargs):
        # 옵션 1: 태스크 직접 호출
        result = test_task.delay()
        self.stdout.write(self.style.SUCCESS(f"테스트 태스크 큐에 추가됨. 태스크 ID: {result.id}"))