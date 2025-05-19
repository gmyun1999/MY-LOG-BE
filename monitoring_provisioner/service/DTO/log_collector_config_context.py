from dataclasses import dataclass


@dataclass
class LogCollectorConfigContext:
    """
    collector 설정을 렌더링할 때
    필요한 모든 파라미터를 모아놓은 DTO.
    """
    project_id: str             # 모니터링 대상 프로젝트 식별자
    hosts: list[str]            # 수집할 대상 호스트 목록 (e.g. ["10.0.0.1:5044", ...])
    log_paths: list[str]        # 수집할 로그 파일 경로들
    index_name: str             # Elasticsearch 인덱스 이름
    tags: list[str] | None = None      # Filebeat 태그
    extra_vars: dict | None = None     # 템플릿 내 추가 변수 (필요시)
