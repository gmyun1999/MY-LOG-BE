from typing import Dict, List, Optional, Any

from monitoring_provisioner.domain.grafana_dashboard import GrafanaDashboard
from monitoring_provisioner.domain.i_repository.i_grafana_repo import IGrafanaRepository
from monitoring_provisioner.infra.grafana.grafana_api import GrafanaAPI


class GrafanaRepository(IGrafanaRepository):
    def __init__(self):
        self.api = GrafanaAPI()
    
    def create_folder(self, user_id: str, folder_name: str) -> str:
        """
        사용자 전용 폴더 생성
        - folder 명은 "User_{user_id}_{folder_name}" 형식으로 조합
        - API 호출 후 응답의 'uid' 값을 반환
        """
        response = self.api.create_folder(f"User_{user_id}_{folder_name}")
        return response["uid"]
    
    def create_service_account(self, name: str, role: str) -> dict:
        """
        Grafana 서비스 계정 생성
        - name: 서비스 계정 식별자
        - role: Viewer, Editor, Admin 중 선택
        - API 응답 전체(dict) 반환
        """
        return self.api.create_service_account(name, role)
    
    def create_service_token(self, service_account_id: int, token_name: str) -> dict:
        """
        서비스 계정용 API 토큰 발급
        - service_account_id: 토큰을 발급할 계정의 내부 ID
        - token_name: 토큰 식별용 이름
        - API 응답 전체(dict) 반환
        """
        return self.api.create_service_token(service_account_id, token_name)
    
    def set_folder_permissions(self, folder_uid: str, service_account_id: int) -> bool:
        """
        폴더 권한 설정
        - folder_uid: 권한을 설정할 폴더의 UID
        - service_account_id: 권한을 부여할 서비스 계정 ID
        - 성공 시 True 반환 (실제 실패 처리는 예외로 발생)
        """
        self.api.set_folder_permissions(folder_uid, service_account_id)
        return True
    
    def create_dashboard(self, dashboard: GrafanaDashboard) -> GrafanaDashboard:
        """
        대시보드 생성
        1. 도메인 객체를 Grafana API 페이로드 형태로 변환
        2. API 호출로 대시보드 생성
        3. 응답에서 uid, url을 도메인 객체에 갱신 후 반환
        """
        dashboard_data = {
            "title": dashboard.title,
            "uid": dashboard.uid,
            "tags": dashboard.tags,
            "panels": dashboard.panels
        }
        
        response = self.api.create_dashboard(dashboard_data, dashboard.folder_uid)
        
        # 응답 데이터로 도메인 객체 업데이트
        dashboard.uid = response["uid"]
        dashboard.url = response["url"]
        
        return dashboard
    
    def get_dashboard_by_uid(self, uid: str) -> Optional[GrafanaDashboard]:
        """
        UID로 대시보드 조회
        - API 호출 후 응답에서 필요한 필드만 추출하여 도메인 객체 생성
        - 조회 실패 시 None 반환
        """
        try:
            response = self.api.get_dashboard(uid)
            
            dashboard = GrafanaDashboard(
                uid=response["dashboard"]["uid"],
                title=response["dashboard"]["title"],
                folder_uid=response.get("meta", {}).get("folderUid"),
                url=response.get("meta", {}).get("url"),
                panels=response["dashboard"].get("panels", []),
                tags=response["dashboard"].get("tags", [])
            )
            
            return dashboard
        except Exception:
            return None
    
    def get_dashboards_by_user(self, user_id: str) -> List[GrafanaDashboard]:
        """
        사용자 소유 대시보드 목록 조회 (미구현 상태)
        - 실제 Grafana 검색 API 활용하여 구현
        """
        return []