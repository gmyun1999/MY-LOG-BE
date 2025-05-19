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
    
    def create_service_account(self, name: str, role: str = None) -> Dict[str, Any]:
        """
        서비스 계정 생성
        그라파나 12.0.0 버전 호환
        """
        url = f"{self.base_url}/api/serviceaccounts"
        
        # 그라파나 12.0.0 API 형식에 맞게 조정
        data = {
            "name": name,
        }
        
        # role이 제공된 경우에만 추가
        if role:
            data["role"] = role
        
        try:
            print(f"서비스 계정 생성 요청: URL={url}, 데이터={data}")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            print(f"서비스 계정 생성 응답: 상태 코드={response.status_code}, 응답={response.text}")
            
            # 성공한 경우 응답 반환
            if response.status_code in [200, 201]:
                return response.json()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"서비스 계정 생성 예외: {str(e)}")
            raise
    
    def create_service_token(self, service_account_id: int, token_name: str) -> Dict[str, Any]:
        """
        서비스 계정 토큰 생성
        """
        url = f"{self.base_url}/api/serviceaccounts/{service_account_id}/tokens"
        data = {"name": token_name}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def set_folder_permissions(self, folder_uid: str, service_account_id: int, permission: int = 1) -> Dict[str, Any]:
        """
        폴더 권한 설정
        그라파나 12.0.0 버전 호환
        """
        url = f"{self.base_url}/api/folders/{folder_uid}/permissions"
        
        # 그라파나 12.0.0 버전에 맞는 형식
        data = {
            "items": [
                {"role": "Viewer", "permission": 0},  # 기존 권한 제거
                {"serviceAccountId": service_account_id, "permission": permission}
            ]
        }
        
        try:
            print(f"폴더 권한 설정 요청: URL={url}, 데이터={data}")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            print(f"폴더 권한 설정 응답: 상태 코드={response.status_code}, 응답={response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            
            # 오류 시 대체 형식 시도
            if response.status_code >= 400:
                print("대체 권한 설정 형식 시도...")
                alt_data = {
                    "items": [
                        {"role": "Viewer", "permission": 0},
                        {"userId": service_account_id, "permission": permission}
                    ]
                }
                alt_response = requests.post(url, json=alt_data, headers=self.headers)
                print(f"대체 폴더 권한 설정 응답: 상태 코드={alt_response.status_code}, 응답={alt_response.text}")
                
                if alt_response.status_code in [200, 201]:
                    return alt_response.json()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"폴더 권한 설정 예외: {str(e)}")
            raise
        
    def create_dashboard(self, dashboard_data: Dict[str, Any], folder_uid: str = None) -> Dict[str, Any]:
        """
        대시보드 생성
        """
        url = f"{self.base_url}/api/dashboards/db"
        data = {
            "dashboard": dashboard_data,
            "overwrite": True
        }
        
        # 중요: folderUid가 있을 때만 추가 (빈 문자열이나 None이 아닐 때)
        if folder_uid:
            data["folderUid"] = folder_uid
            print(f"대시보드를 폴더 {folder_uid}에 생성합니다.")
        else:
            print("폴더 UID가 없어 루트에 대시보드를 생성합니다.")
        
        print(f"대시보드 생성 API 요청: {url}, 데이터: {data}")
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code >= 400:
            print(f"대시보드 생성 오류: {response.status_code}, 응답: {response.text}")
        
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
    
    def get_folders(self) -> List[Dict[str, Any]]:
        """
        그라파나 폴더 목록 조회
        """
        url = f"{self.base_url}/api/folders"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            # 디버깅 로그
            print(f"폴더 목록 조회 응답: 상태 코드={response.status_code}")
            
            if response.status_code >= 400:
                print(f"폴더 목록 조회 오류: {response.status_code}, 응답: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"폴더 목록 조회 예외: {str(e)}")
            # 오류 발생 시 빈 리스트 반환
            return []