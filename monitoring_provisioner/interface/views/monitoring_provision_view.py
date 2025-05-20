from dataclasses import dataclass

from django.http import HttpRequest
from pydantic import BaseModel, Field
from rest_framework import status
from rest_framework.views import APIView

from common.interface.validators import validate_body
from user.interface.validator.user_token_validator import validate_token


class MonitoringProvisionView(APIView):
    @dataclass
    class UserMonitoringSetting(BaseModel):
        pass

    def __init__(self):
        pass

    """
    모니터링 프로젝트 생성
    """

    @validate_token()
    @validate_body(UserMonitoringSetting)
    def post(self, request: HttpRequest, body: UserMonitoringSetting):
        """
        가져온 모니터링 설정을 기반으로 모니터링 프로젝트를 생성함
        1. 일단 관련 정보를 모니터링 관련 DB에 저장
        2. 정보를 바탕으로 worker에게 프로비저닝 요청
        3. worker은 완료되면 result bakend에 저장 (redis 및 rdbms)
        4. 실패하더라도 모니터링 관련 DB의 데이터는 삭제하지않음
        response의 경우 모니터링 관련 DB에 저장이후 task 등록후 바로 return
        프로비저닝 진행 상황은 별도의 api를 통해 확인 가능
        """
        pass
