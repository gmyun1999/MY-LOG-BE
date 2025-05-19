from abc import ABC, abstractmethod

class IStorageProvider(ABC):
    @abstractmethod
    def upload(
        self,
        data: bytes,
        key: str,
        content_type: str = 'application/octet-stream'
    ) -> str:
        """
        바이트 데이터를 저장하고, 외부에서 접근 가능한 URL을 반환

        :param data: 업로드할 바이트 데이터
        :param key: S3 버킷 내 저장 경로 (예: "projectA/config.yml")
        :param content_type: 업로드할 객체의 MIME 타입 (기본값: application/octet-stream)
        :return: 저장된 객체의 public URL
        """
        ...