from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from monitoring_provisioner.domain.visualization_platform.dashboard import Dashboard


class MonitoringDashboardExecutor(ABC):
    @abstractmethod
    def create_user_folder(self, user_id: str, user_name: str) -> str:
        """
        사용자 폴더 생성
        :param user_id: 사용자 ID
        :param user_name: 사용자 이름
        :return: 생성된 폴더 UID
        """
        pass

    @abstractmethod
    def create_service_account(self, user_id: str) -> Dict:
        """
        사용자별 서비스 계정 생성
        :param user_id: 사용자 ID
        :return: 서비스 계정 정보와 토큰
        """
        pass

    @abstractmethod
    def create_dashboard(self, user_id: str, title: str, panels: List = None) -> None:
        """
        대시보드 생성 작업 큐에 등록
        :param user_id: 사용자 ID
        :param title: 대시보드 제목
        :param panels: 패널 목록
        :return: None
        """
        pass

    # @abstractmethod
    # def get_dashboard(self, dashboard_uid: str) -> Optional[Dashboard]:
    #     """
    #     대시보드 정보 조회
    #     :param dashboard_uid: 대시보드 UID
    #     :return: 대시보드 객체
    #     """
    #     pass

    # @abstractmethod
    # def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
    #     """
    #     사용자 대시보드 목록 조회
    #     :param user_id: 사용자 ID
    #     :return: 대시보드 객체 리스트
    #     """
    #     pass
