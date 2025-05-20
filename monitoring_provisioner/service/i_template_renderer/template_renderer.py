from abc import ABC, abstractmethod

class ITemplateRenderer(ABC):
    @abstractmethod
    def render(self, template_name: str, context: dict) -> str:
        """
        주어진 템플릿 이름과 컨텍스트를 사용하여 렌더링된 텍스트를 반환
        :param template_name: 템플릿 파일 이름
        :param context: 템플릿에 전달할 데이터
        :return: 렌더링된 텍스트
        """
        ...