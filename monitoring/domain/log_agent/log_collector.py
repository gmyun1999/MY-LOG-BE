from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class LogInputType(StrEnum):
    PLAIN = "PLAIN"
    JSON = "JSON"


class FilterOperator(StrEnum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"


class JsonFieldMapping(BaseModel):
    name: str
    json_path: str | None = None


class FilterCondition(BaseModel):
    field: str
    operator: FilterOperator
    value: str


class PlainRequiredField(StrEnum):
    MSG_DETAIL = "msg_detail"
    LEVEL = "level"
    TIMESTAMP = "timestamp"
    DATE = "date"
    TIME = "time"


class LogCollectorConfigContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    FIELD_PROJECT_ID: str = "project_id"
    FIELD_HOSTS: str = "hosts"
    FIELD_LOG_PATHS: str = "log_paths"

    FIELD_MULTILINE_PATTERN: str = "multiline_pattern"

    FIELD_TIMESTAMP_FIELD: str = "timestamp_field"  # json 로그의 타임스템프 필드
    FIELD_TIMESTAMP_JSON_PATH: str = (
        "timestamp_json_path"  # json 로그의 타임스탬프 필드 경로
    )

    FIELD_LOG_LEVEL: str = "log_level"  # json 로그의 로그 레벨 필드
    FIELD_LOG_LEVEL_JSON_PATH: str = (
        "log_level_json_path"  # json 로그의 로그 레벨 필드 경로
    )

    FIELD_CUSTOM_JSON_FIELDS: str = "custom_json_fields"  # 사용자 정의 json 필드

    FIELD_FILTERS: str = "filters"

    project_id: str
    hosts: list[str]
    log_paths: list[str]
    input_type: LogInputType

    # <plain 전용>
    multiline_pattern: str | None = None
    custom_plain_fields: list[str] = []

    # <json 전용>
    # 필수 필드
    timestamp_field: str | None = None
    timestamp_json_path: str | None = None
    log_level: str | None = None
    log_level_json_path: str | None = None
    # 사용자 정의 필드드
    custom_json_fields: list[JsonFieldMapping] = []

    # 공통
    filters: list[FilterCondition] = []

    @model_validator(mode="after")
    def check_input_specific(self) -> "LogCollectorConfigContext":
        if self.input_type is LogInputType.PLAIN:
            # custom_plain_fields 필수
            if not self.custom_plain_fields:
                raise ValueError("plain text 타입에는 custom_plain_fields 필수")

            fields_set = set(self.custom_plain_fields)

            required = {
                PlainRequiredField.MSG_DETAIL.value,
                PlainRequiredField.LEVEL.value,
            }
            missing_required = required - fields_set
            if missing_required:
                raise ValueError(
                    f"plain text 타입에는 {', '.join(missing_required)} 필드가 필요합니다"
                )

            ts = PlainRequiredField.TIMESTAMP.value
            date_time = {
                PlainRequiredField.DATE.value,
                PlainRequiredField.TIME.value,
            }
            has_ts = ts in fields_set
            has_date_time = date_time.issubset(fields_set)

            if not (has_ts ^ has_date_time):
                raise ValueError(
                    "plain text 타입에는 'timestamp' 또는 'date'와 'time'이 둘 다 필요하며, "
                    "두 조건을 동시에 가질 수 없습니다"
                )

            # json 전용 필드 사용 불가
            forbidden_json = [
                self.timestamp_field,
                self.timestamp_json_path,
                self.log_level,
                self.log_level_json_path,
                self.custom_json_fields,
            ]
            if any(forbidden_json):
                raise ValueError(
                    "plain text 타입에는 JSON 전용 필드를 사용할 수 없습니다"
                )

        else:
            # JSON 타입 필수 검증
            if not self.timestamp_field:
                raise ValueError("json 타입에는 timestamp_field 필수")
            if not self.timestamp_json_path:
                raise ValueError("json 타입에는 timestamp_json_path 필수")
            if not self.log_level:
                raise ValueError("json 타입에는 log_level 필수")
            if not self.log_level_json_path:
                raise ValueError("json 타입에는 log_level_json_path 필수")
        return self
