from abc import ABC, abstractmethod
from typing import Optional, List

from monitoring_provisioner.domain.grafana_dashboard import GrafanaDashboard


class IGrafanaRepository(ABC):
    @abstractmethod
    def create_folder(self, user_id: str, folder_name: str) -> str:
        """
        사용자 전용 폴더를 생성한 뒤, 그 UID를 반환
        :param user_id: 대시보드를 소유할 사용자 식별자
        :param folder_name: 생성할 폴더의 이름
        :return: 새로 생성된 폴더의 UID 문자열
        """
        pass
    
    @abstractmethod
    def create_service_account(self, name: str, role: str) -> dict:
        """
        Grafana 내에서 사용할 서비스 계정을 생성
        :param name: 서비스 계정 이름
        :param role: 부여할 역할 (예: Viewer, Editor, Admin)
        :return: 생성된 계정의 상세 정보를 담은 dict
        """
        pass
    
    @abstractmethod
    def create_service_token(self, service_account_id: int, token_name: str) -> dict:
        """
        서비스 계정에 대한 API 토큰을 발급
        :param service_account_id: 서비스 계정의 내부 ID
        :param token_name: 토큰 식별용 이름
        :return: 토큰 정보 (토큰 문자열, 만료일 등)을 담은 dict
        """
        pass
    
    @abstractmethod
    def set_folder_permissions(self, folder_uid: str, service_account_id: int) -> bool:
        """
        특정 폴더에 대해 서비스 계정의 권한을 설정
        :param folder_uid: 권한을 설정할 폴더의 UID
        :param service_account_id: 권한을 부여할 서비스 계정 ID
        :return: 권한 설정 성공 여부 (True/False)
        """
        pass
    
    @abstractmethod
    def create_dashboard(self, dashboard: GrafanaDashboard) -> GrafanaDashboard:
        """
        Grafana API를 통해 대시보드를 생성
        :param dashboard: 생성할 대시보드 정보가 담긴 도메인 객체
        :return: API 응답으로 반환된 실제 생성된 대시보드 객체
        """
        pass
    
    @abstractmethod
    def get_dashboard_by_uid(self, uid: str) -> Optional[GrafanaDashboard]:
        """
        UID로 대시보드를 조회
        :param uid: 대시보드의 고유 UID
        :return: 해당 대시보드가 존재하면 GrafanaDashboard 객체, 없으면 None
        """
        pass
    
    @abstractmethod
    def get_dashboards_by_user(self, user_id: str) -> List[GrafanaDashboard]:
        """
        특정 사용자가 소유한 모든 대시보드를 조회
        :param user_id: 사용자 식별자
        :return: GrafanaDashboard 객체 리스트
        """
        pass