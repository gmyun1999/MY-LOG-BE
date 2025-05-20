from pydantic import BaseModel
import base64

class RenderedConfigFile(BaseModel):
    """
    렌더링된 설정 파일을 표현하는 도메인 객체.
    - filename: 저장 또는 업로드 시 사용할 파일명
    - content: 파일의 바이너리 컨텐츠
    """
    filename: str
    content: bytes

    @property
    def base64(self) -> str:
        return base64.b64encode(self.content).decode("ascii")