from dataclasses import dataclass
from typing import List, Dict, Any
from django.http import HttpRequest
from pydantic import BaseModel, Field
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.interface.validators import validate_body
from user.interface.validator.user_token_validator import validate_token
from monitoring_provisioner.infra.celery.executor.grafana_executor import GrafanaExecutor


class MonitoringProvisionView(APIView):
    """
    모니터링 프로젝트 생성 및 조회를 처리하는 뷰
    - POST 요청: 사용자 폴더 생성 및 대시보드 생성 태스크 등록
    - GET 요청: 특정 사용자의 대시보드 목록 조회
    """
    class UserMonitoringSetting(BaseModel):
        """
        POST 요청 본문 검증용 스키마
        - user_id: 사용자 식별자
        - user_name: 사용자 이름
        - dashboard_title: 생성할 대시보드 제목 (옵션)
        - panels: 대시보드에 포함할 패널 설정 목록
        - data_sources: 대시보드에서 사용할 데이터 소스 목록
        """
        user_id: str = Field(..., description="사용자 ID")
        user_name: str = Field(..., description="사용자 이름")
        dashboard_title: str = Field(None, description="대시보드 제목")
        panels: List[Dict[str, Any]] = Field(default_factory=list, description="패널 설정")
        data_sources: List[str] = Field(default_factory=list, description="데이터 소스 목록")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = GrafanaExecutor()

    """
    모니터링 프로젝트 생성
    """
    @validate_token()
    @validate_body(UserMonitoringSetting)
    def post(self, request: HttpRequest, body: UserMonitoringSetting):
        """
        모니터링 프로젝트 생성 엔드포인트
        1. 사용자 전용 폴더 생성 태스크 등록 (비동기)
        2. 대시보드 생성 태스크 등록 (비동기)
        3. 등록된 첫 번째 태스크 ID를 클라이언트에 반환
        """
        # 1. 사용자 폴더 생성 태스크 등록
        task_id = self.executor.create_user_folder(body.user_id, body.user_name)
        
        # 2. 대시보드 생성 태스크 등록
        self.executor.create_dashboard(
            user_id=body.user_id,
            title=body.dashboard_title or f"{body.user_name}의 대시보드",
            panels=body.panels
        )
        
        # 202 Accepted: 요청은 성공적으로 접수되었으나 아직 처리 중임
        return Response({
            "message": "모니터링 프로젝트 생성 요청이 등록되었습니다.",
            "task_id": task_id
        }, status=status.HTTP_202_ACCEPTED)
    
    """
    사용자 대시보드 목록 조회
    """
    @validate_token()
    def get(self, request: HttpRequest):
        """
        사용자 대시보드 목록 조회 엔드포인트
        - user_id 쿼리 파라미터를 필요로 함
        - 없으면 400 Bad Request 반환
        - 있으면 Grafana로부터 대시보드 리스트 조회 후 반환
        """
        user_id = request.GET.get("user_id")
        
        if not user_id:
            return Response({
                "error": "user_id parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Grafana에서 사용자 소유 대시보드 조회
        dashboards = self.executor.get_user_dashboards(user_id)
        
        # 도메인 객체를 API 응답용 dict 리스트로 변환
        return Response({
            "dashboards": [
                {
                    "uid": d.uid,
                    "title": d.title,
                    "url": d.url
                } for d in dashboards
            ]
        })