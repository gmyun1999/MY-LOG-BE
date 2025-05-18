import os
import requests
from typing import Dict, List, Optional, Any
from config.settings import GRAFANA_URL, GRAFANA_ADMIN_API_KEY


class GrafanaAPI:
    def __init__(self):
        # 직접 설정에서 가져오기
        self.base_url = GRAFANA_URL
        self.admin_api_key = GRAFANA_ADMIN_API_KEY
        
        # Docker URL을 로컬 테스트용 URL로 변환 (필요시)
        if "grafana:3000" in self.base_url and not os.environ.get("DOCKER_ENV"):
            self.base_url = "http://localhost:3000"
            
        self.headers = {
            "Authorization": f"Bearer {self.admin_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_folder(self, title: str) -> Dict[str, Any]:
        """
        그라파나 폴더 생성
        """
        url = f"{self.base_url}/api/folders"
        data = {"title": title}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_service_account(self, name: str, role: str = "Viewer") -> Dict[str, Any]:
        """
        서비스 계정 생성
        """
        url = f"{self.base_url}/api/serviceaccounts"
        data = {"name": name, "role": role}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_service_token(self, service_account_id: int, token_name: str) -> Dict[str, Any]:
        """
        서비스 계정 토큰 생성
        """
        url = f"{self.base_url}/api/serviceaccounts/{service_account_id}/tokens"
        data = {"name": token_name}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def set_folder_permissions(self, folder_uid: str, service_account_id: int, 
                               permission: int = 1) -> Dict[str, Any]:
        """
        폴더 권한 설정
        permission: 1=Viewer, 2=Editor, 4=Admin
        """
        url = f"{self.base_url}/api/folders/{folder_uid}/permissions"
        data = {
            "items": [
                {"role": "Viewer", "permission": 0},  # 기존 권한 제거
                {"serviceAccountId": service_account_id, "permission": permission}
            ]
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_dashboard(self, dashboard_data: Dict[str, Any], folder_uid: str = None) -> Dict[str, Any]:
        """
        대시보드 생성
        """
        url = f"{self.base_url}/api/dashboards/db"
        data = {
            "dashboard": dashboard_data,
            "overwrite": True
        }
        
        if folder_uid:
            data["folderUid"] = folder_uid
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        대시보드 정보 조회
        """
        url = f"{self.base_url}/api/dashboards/uid/{uid}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def generate_dashboard_url(self, uid: str, token: str) -> str:
        """
        인증된 대시보드 URL 생성
        """
        return f"{self.base_url}/d/{uid}?orgId=1&from=now-6h&to=now&auth_token={token}"