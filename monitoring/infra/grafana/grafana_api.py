from typing import Any

import requests
from typing_extensions import override

from config.settings import GRAFANA_ADMIN_API_KEY, GRAFANA_URL
from monitoring.service.i_visualization_platform.i_visualization_platform_provider import (
    VisualizationPlatformProvider,
)


class GrafanaAPI(VisualizationPlatformProvider):
    def __init__(self):

        self.base_url = GRAFANA_URL
        self.admin_api_key = GRAFANA_ADMIN_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.admin_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @override
    def create_folder(self, title: str) -> dict[str, Any]:
        """
        그라파나 폴더 생성
        param title: 폴더 제목
        """
        url = f"{self.base_url}/api/folders"
        data = {"title": title}

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def create_service_account(self, name: str, role: str = "Viewer") -> dict[str, Any]:
        """
        서비스 계정 생성
        그라파나 12.0.0 버전 호환
        """
        url = f"{self.base_url}/api/serviceaccounts"

        # 그라파나 12.0.0 API 형식에 맞게 조정
        data = {"name": name, "role": role, "isDisabled": False}

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def create_service_token(
        self, service_account_id: int, token_name: str
    ) -> dict[str, Any]:
        """
        서비스 계정 토큰 생성
        param service_account_id: 그라파나의 서비스 계정 ID
        return: token
        """
        url = f"{self.base_url}/api/serviceaccounts/{service_account_id}/tokens"
        data = {"name": token_name}

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def set_folder_permissions(
        self, folder_uid: str, service_account_id: int, permission: int = 1
    ) -> dict[str, Any]:
        """
        폴더 권한 설정 - Grafana 12.0.0 버전용
        """
        url = f"{self.base_url}/api/folders/{folder_uid}/permissions"

        # Grafana 12 호환 형식으로
        data = {"items": [{"userId": service_account_id, "permission": permission}]}

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def create_dashboard(
        self, dashboard_data: dict[str, Any], folder_uid: str
    ) -> dict[str, Any]:
        """
        대시보드 생성
        """
        url = f"{self.base_url}/api/dashboards/db"
        data = {
            "dashboard": dashboard_data,
            "overwrite": True,
            "folderUid": folder_uid,
        }

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        return response.json()

    @override
    def create_public_dashboard(self, dashboard_uid: str) -> dict[str, Any]:
        """
        퍼블릭 대시보드 생성 - 대시보드 UID를 받아 해당 대시보드의 퍼블릭 버전 생성
        생성된 퍼블릭 대시보드의 정보(UID, accessToken 등) 반환
        """
        url = f"{self.base_url}/api/dashboards/uid/{dashboard_uid}/public-dashboards"
        data = {
            "isEnabled": True,
            "timeSelectionEnabled": True,
            "annotationsEnabled": True,
            "share": "public",  # 'public' 또는 'withToken'
        }

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def get_folders(self) -> list[dict[str, Any]]:
        """
        view 권한을 가진 그라파나 폴더 목록 조회
        """
        url = f"{self.base_url}/api/folders"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    @override
    def get_public_dashboard(self, public_dashboard_uid: str) -> dict[str, Any]:
        """
        퍼블릭 대시보드 정보 조회
        """
        url = f"{self.base_url}/api/public-dashboards/{public_dashboard_uid}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @override
    def get_dashboard(self, uid: str) -> dict[str, Any]:
        """
        대시보드 정보 조회
        """
        url = f"{self.base_url}/api/dashboards/uid/{uid}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    @override
    def generate_dashboard_url(self, uid: str, token: str) -> str:
        """
        인증된 대시보드 URL 생성
        """
        return f"{self.base_url}/d/{uid}?orgId=1&from=now-6h&to=now&auth_token={token}"
