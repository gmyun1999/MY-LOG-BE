from abc import ABC, abstractmethod


class IAgentStorageProvider(ABC):
    @abstractmethod
    def upload(
        self, data: bytes, key: str, content_type: str = "application/octet-stream"
    ) -> str:
        """
        지정된 키에 데이터를 업로드하고, 외부에서 접근 가능한 URL을 반환한다.

        :param data: 업로드할 바이트 데이터
        :param key: 저장소 내 경로 키 (예: "projectA/config.yml")
        :param content_type: 콘텐츠 타입 (MIME), 기본값은 application/octet-stream
        :return: 업로드된 파일에 접근 가능한 URL
        """
        ...

    @abstractmethod
    def get_object_url(self, key: str) -> str:
        """
        실제 업로드 없이, 주어진 키에 대해 접근 가능한 URL을 계산하여 반환한다.

        :param key: 저장소 내 경로 키
        :return: 예상 접근 URL
        """
        ...

    @abstractmethod
    def get_object_key(self, resource_id: str, ts: int, filename: str) -> str:
        """
        리소스 ID, 타임스탬프, 파일명을 기반으로 고유한 저장 키를 생성한다.

        :param resource_id: 리소스를 식별하는 ID
        :param ts: 타임스탬프 또는 버전 구분용 값
        :param filename: 저장할 파일 이름
        :return: 저장소 내 고유 경로 키
        """
        ...

    @abstractmethod
    def get_base_static_url(self) -> str:
        """
        공통 정적 파일이 위치하는 저장소 base URL을 반환한다.

        :return: 정적 자산 base URL (예: "https://.../harvester")
        """
        ...
