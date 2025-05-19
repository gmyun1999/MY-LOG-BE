from dataclasses import dataclass

@dataclass
class GeneratedConfig:
    """
    단일 파일 정보.
    - filename: 업로드/저장 시 사용할 파일명 (예: "collector.yml")
    - content: 실제 파일 바이트 데이터
    """
    filename: str
    content: bytes

    @property
    def base64(self) -> str:
        """
        필요하면 HTTP API 레이어에서 JSON으로 넘길 때
        안전하게 인코딩할 수 있도록 base64 문자열로 제공
        """
        import base64
        return base64.b64encode(self.content).decode('ascii')
