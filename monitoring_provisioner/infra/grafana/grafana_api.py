import os
import requests
from typing import Dict, List, Optional, Any
from config.settings import GRAFANA_URL, GRAFANA_ADMIN_API_KEY


class GrafanaAPI:
    def __init__(self):
        # 직접 설정에서 가져오기
        self.base_url = GRAFANA_URL
        self.admin_api_key = GRAFANA_ADMIN_API_KEY
        
        # Docker URL을 로컬 테스트용 URL로 변환 (필요시)
        if "grafana:3000" in self.base_url and not os.environ.get("DOCKER_ENV"):
            self.base_url = "http://localhost:3000"
            
        self.headers = {
            "Authorization": f"Bearer {self.admin_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_folder(self, title: str) -> Dict[str, Any]:
        """
        그라파나 폴더 생성
        """
        url = f"{self.base_url}/api/folders"
        data = {"title": title}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_service_account(self, name: str, role: str = None) -> Dict[str, Any]:
        """
        서비스 계정 생성
        그라파나 12.0.0 버전 호환
        """
        url = f"{self.base_url}/api/serviceaccounts"
        
        # 그라파나 12.0.0 API 형식에 맞게 조정
        data = {
            "name": name,
        }
        
        # role이 제공된 경우에만 추가
        if role:
            data["role"] = role
        
        try:
            print(f"서비스 계정 생성 요청: URL={url}, 데이터={data}")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            print(f"서비스 계정 생성 응답: 상태 코드={response.status_code}, 응답={response.text}")
            
            # 성공한 경우 응답 반환
            if response.status_code in [200, 201]:
                return response.json()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"서비스 계정 생성 예외: {str(e)}")
            raise
    
    def create_service_token(self, service_account_id: int, token_name: str) -> Dict[str, Any]:
        """
        서비스 계정 토큰 생성
        """
        url = f"{self.base_url}/api/serviceaccounts/{service_account_id}/tokens"
        data = {"name": token_name}
        
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def set_folder_permissions(self, folder_uid: str, service_account_id: int, permission: int = 1) -> Dict[str, Any]:
        """
        폴더 권한 설정 - Grafana 12.0.0 버전용 수정
        """
        url = f"{self.base_url}/api/folders/{folder_uid}/permissions"
        
        # Grafana 12 호환 형식으로
        data = {
            "items": [
                {"userId": service_account_id, "permission": permission}
            ]
        }
        
        try:
            print(f"폴더 권한 설정 요청: URL={url}, 데이터={data}")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            print(f"폴더 권한 설정 응답: 상태 코드={response.status_code}, 응답={response.text}")
            
            if response.status_code in [200, 201]:
                return response.json()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"폴더 권한 설정 예외: {str(e)}")
            raise
        
    def create_dashboard(self, dashboard_data: Dict[str, Any], folder_uid: str = None) -> Dict[str, Any]:
        """
        대시보드 생성
        """
        url = f"{self.base_url}/api/dashboards/db"
        data = {
            "dashboard": dashboard_data,
            "overwrite": True
        }
        
        # 중요: folderUid가 있을 때만 추가 (빈 문자열이나 None이 아닐 때)
        if folder_uid:
            data["folderUid"] = folder_uid
            print(f"대시보드를 폴더 {folder_uid}에 생성합니다.")
        else:
            print("폴더 UID가 없어 루트에 대시보드를 생성합니다.")
        
        print(f"대시보드 생성 API 요청: {url}, 데이터: {data}")
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code >= 400:
            print(f"대시보드 생성 오류: {response.status_code}, 응답: {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        대시보드 정보 조회
        """
        url = f"{self.base_url}/api/dashboards/uid/{uid}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def generate_dashboard_url(self, uid: str, token: str) -> str:
        """
        인증된 대시보드 URL 생성
        """
        return f"{self.base_url}/d/{uid}?orgId=1&from=now-6h&to=now&auth_token={token}"
    
    def get_folders(self) -> List[Dict[str, Any]]:
        """
        그라파나 폴더 목록 조회
        """
        url = f"{self.base_url}/api/folders"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            # 디버깅 로그
            print(f"폴더 목록 조회 응답: 상태 코드={response.status_code}")
            
            if response.status_code >= 400:
                print(f"폴더 목록 조회 오류: {response.status_code}, 응답: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"폴더 목록 조회 예외: {str(e)}")
            # 오류 발생 시 빈 리스트 반환
            return []
        
    def create_public_dashboard(self, dashboard_uid: str) -> Dict[str, Any]:
        """
        퍼블릭 대시보드 생성 - 대시보드 UID를 받아 해당 대시보드의 퍼블릭 버전 생성
        생성된 퍼블릭 대시보드의 정보(UID, accessToken 등) 반환
        """
        url = f"{self.base_url}/api/dashboards/uid/{dashboard_uid}/public-dashboards"
        data = {
            "isEnabled": True,
            "timeSelectionEnabled": True,
            "annotationsEnabled": True,
            "share": "public"  # 'public' 또는 'withToken'
        }
        
        print(f"퍼블릭 대시보드 생성 요청: URL={url}, 데이터={data}")
        
        response = requests.post(url, json=data, headers=self.headers)
        
        print(f"퍼블릭 대시보드 생성 응답: 상태 코드={response.status_code}, 응답={response.text}")
        
        if response.status_code >= 400:
            print(f"퍼블릭 대시보드 생성 오류: {response.status_code}, 응답: {response.text}")
        
        response.raise_for_status()
        return response.json()

    def get_public_dashboard(self, public_dashboard_uid: str) -> Dict[str, Any]:
        """
        퍼블릭 대시보드 정보 조회
        """
        url = f"{self.base_url}/api/public-dashboards/{public_dashboard_uid}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def generate_public_dashboard_url(self, public_dashboard_result: Dict[str, Any]) -> str:
        """
        API 응답 바탕으로 접근 가능한 퍼블릭 대시보드 URL 생성
        """
        if isinstance(public_dashboard_result, dict):
            if 'accessToken' in public_dashboard_result:
                # API 응답 형식 사용 (accessToken 사용) -> 이게 작동
                return f"{self.base_url}/public-dashboards/{public_dashboard_result['accessToken']}"
        
        # 기본값 또는 오류 시
        return None
    

    def create_logs_dashboard(self, user_id: str, user_name: str, folder_uid: str = None, 
                            data_source_uid: str = "Elasticsearch") -> Dict[str, Any]:
        """
        Elasticsearch 로그 대시보드 생성
        사용자별 로그 필터링을 위한 대시보드를 생성
        """
        # 대시보드 UID 생성 (사용자 ID 기반)
        dashboard_uid = f"logs-dashboard-{user_id}"
        
        # 대시보드 템플릿 기본 구조
        dashboard_data = {
            "annotations": {
                "list": [
                    {
                        "builtIn": 1,
                        "datasource": {
                            "type": "grafana",
                            "uid": "-- Grafana --"
                        },
                        "enable": True,
                        "hide": True,
                        "iconColor": "rgba(0, 211, 255, 1)",
                        "name": "Annotations & Alerts",
                        "type": "dashboard"
                    }
                ]
            },
            "editable": True,
            "fiscalYearStartMonth": 0,
            "graphTooltip": 0,
            "links": [],
            "panels": [
                # 시계열 차트 패널
                {
                    "datasource": {
                        "type": "elasticsearch",
                        "uid": data_source_uid
                    },
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "palette-classic"
                            },
                            "custom": {
                                "axisBorderShow": False,
                                "axisCenteredZero": False,
                                "axisColorMode": "text",
                                "axisLabel": "",
                                "axisPlacement": "auto",
                                "barAlignment": 0,
                                "barWidthFactor": 0.6,
                                "drawStyle": "line",
                                "fillOpacity": 10,
                                "gradientMode": "none",
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "viz": False
                                },
                                "insertNulls": False,
                                "lineInterpolation": "linear",
                                "lineWidth": 1,
                                "pointSize": 5,
                                "scaleDistribution": {
                                    "type": "linear"
                                },
                                "showPoints": "never",
                                "spanNulls": False,
                                "stacking": {
                                    "group": "A",
                                    "mode": "normal"
                                },
                                "thresholdsStyle": {
                                    "mode": "off"
                                }
                            },
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "color": "green"
                                    },
                                    {
                                        "color": "red",
                                        "value": 80
                                    }
                                ]
                            },
                            "unit": "short"
                        },
                        "overrides": [
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "INFO"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "green",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "WARN"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "orange",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "ERROR"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "red",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "DEBUG"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "purple",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "WARNING"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "yellow",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    "gridPos": {
                        "h": 8,
                        "w": 24,
                        "x": 0,
                        "y": 0
                    },
                    "id": 3,
                    "options": {
                        "legend": {
                            "calcs": [],
                            "displayMode": "list",
                            "placement": "bottom",
                            "showLegend": True
                        },
                        "tooltip": {
                            "hideZeros": False,
                            "mode": "single",
                            "sort": "none"
                        }
                    },
                    "pluginVersion": "12.0.0",
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "@timestamp",
                                    "id": "2",
                                    "settings": {
                                        "interval": "auto",
                                        "min_doc_count": 0,
                                        "trimEdges": 0
                                    },
                                    "type": "date_histogram"
                                }
                            ],
                            "metrics": [
                                {
                                    "id": "1",
                                    "type": "count"
                                }
                            ],
                            # 중요: 사용자별 필터링 쿼리 추가
                            "query": f"level: $level AND user_id: {user_id}",
                            "refId": "A",
                            "timeField": "@timestamp"
                        }
                    ],
                    "title": "로그 발생 추이",
                    "type": "timeseries"
                },
                # 테이블 패널 (로그 목록)
                {
                    "datasource": {
                        "type": "elasticsearch",
                        "uid": data_source_uid
                    },
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "mode": "thresholds"
                            },
                            "custom": {
                                "align": "auto",
                                "cellOptions": {
                                    "type": "auto"
                                },
                                "filterable": True,
                                "inspect": True
                            },
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {
                                        "color": "green"
                                    },
                                    {
                                        "color": "red",
                                        "value": 80
                                    }
                                ]
                            }
                        },
                        "overrides": [
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "level"
                                },
                                "properties": [
                                    {
                                        "id": "custom.cellOptions",
                                        "value": {
                                            "type": "color-text"
                                        }
                                    },
                                    {
                                        "id": "mappings",
                                        "value": [
                                            {
                                                "options": {
                                                    "DEBUG": {
                                                        "color": "purple",
                                                        "index": 3,
                                                        "text": "DEBUG"
                                                    },
                                                    "ERROR": {
                                                        "color": "red",
                                                        "index": 2,
                                                        "text": "ERROR"
                                                    },
                                                    "INFO": {
                                                        "color": "green",
                                                        "index": 0,
                                                        "text": "INFO"
                                                    },
                                                    "WARN": {
                                                        "color": "orange",
                                                        "index": 1,
                                                        "text": "WARN"
                                                    },
                                                    "WARNING": {
                                                        "color": "yellow",
                                                        "index": 4,
                                                        "text": "WARNING"
                                                    }
                                                },
                                                "type": "value"
                                            }
                                        ]
                                    },
                                    {
                                        "id": "custom.filterable",
                                        "value": True
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "@timestamp"
                                },
                                "properties": [
                                    {
                                        "id": "custom.width",
                                        "value": 200
                                    },
                                    {
                                        "id": "custom.filterable",
                                        "value": True
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "message"
                                },
                                "properties": [
                                    {
                                        "id": "custom.width",
                                        "value": 400
                                    },
                                    {
                                        "id": "custom.filterable",
                                        "value": True
                                    }
                                ]
                            }
                        ]
                    },
                    "gridPos": {
                        "h": 14,
                        "w": 24,
                        "x": 0,
                        "y": 8
                    },
                    "id": 4,
                    "options": {
                        "cellHeight": "sm",
                        "footer": {
                            "countRows": False,
                            "enablePagination": True,
                            "fields": "",
                            "reducer": ["sum"],
                            "show": False
                        },
                        "showHeader": True,
                        "sortBy": [
                            {
                                "desc": False,
                                "displayName": "@timestamp"
                            }
                        ]
                    },
                    "pluginVersion": "12.0.0",
                    "targets": [
                        {
                            "bucketAggs": [],
                            "metrics": [
                                {
                                    "id": "1",
                                    "type": "logs"
                                }
                            ],
                            # 중요: 사용자별 필터링 쿼리 추가
                            "query": f"level: $level AND user_id: {user_id}",
                            "refId": "A",
                            "timeField": "@timestamp"
                        }
                    ],
                    "title": "로그 목록",
                    "transformations": [
                        {
                            "id": "organize",
                            "options": {
                                "excludeByName": {
                                    "_id": True,
                                    "_index": True,
                                    "_source": True,
                                    "_type": True,
                                    "highlight": True,
                                    "host": True,
                                    "pid": True,
                                    "sort": True,
                                    "user_field": True
                                },
                                "indexByName": {
                                    "@timestamp": 0,
                                    "level": 1,
                                    "message": 2,
                                    # "사용자_커스텀_필드1": 3,
                                    # "사용자_커스텀_필드2": 4
                                },
                                "renameByName": {}
                            }
                        }
                    ],
                    "type": "table"
                },
                # 파이 차트 패널 (로그 레벨 분포)
                {
                    "datasource": {
                        "type": "elasticsearch",
                        "uid": data_source_uid
                    },
                    "fieldConfig": {
                        "defaults": {
                            "color": {
                                "fixedColor": "green",
                                "mode": "fixed"
                            },
                            "custom": {
                                "hideFrom": {
                                    "legend": False,
                                    "tooltip": False,
                                    "viz": False
                                }
                            },
                            "mappings": []
                        },
                        "overrides": [
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "INFO"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "green",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "WARN"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "orange",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "ERROR"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "red",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "DEBUG"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "purple",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            },
                            {
                                "matcher": {
                                    "id": "byName",
                                    "options": "WARNING"
                                },
                                "properties": [
                                    {
                                        "id": "color",
                                        "value": {
                                            "fixedColor": "yellow",
                                            "mode": "fixed"
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    "gridPos": {
                        "h": 9,
                        "w": 24,
                        "x": 0,
                        "y": 22
                    },
                    "id": 6,
                    "options": {
                        "displayLabels": ["name", "value", "percent"],
                        "legend": {
                            "displayMode": "table",
                            "placement": "right",
                            "showLegend": True,
                            "values": ["value", "percent"]
                        },
                        "pieType": "pie",
                        "reduceOptions": {
                            "calcs": ["lastNotNull"],
                            "fields": "",
                            "values": True
                        },
                        "tooltip": {
                            "hideZeros": False,
                            "mode": "single",
                            "sort": "none"
                        }
                    },
                    "pluginVersion": "12.0.0",
                    "targets": [
                        {
                            "bucketAggs": [
                                {
                                    "field": "level",
                                    "id": "2",
                                    "settings": {
                                        "min_doc_count": 1,
                                        "order": "desc",
                                        "orderBy": "_count",
                                        "size": "10"
                                    },
                                    "type": "terms"
                                }
                            ],
                            "metrics": [
                                {
                                    "id": "1",
                                    "type": "count"
                                }
                            ],
                            # 중요: 사용자별 필터링 쿼리 추가
                            "query": f"level: $level AND user_id: {user_id}",
                            "refId": "A",
                            "timeField": "@timestamp"
                        }
                    ],
                    "title": "로그 레벨 분포",
                    "type": "piechart"
                }
            ],
            "refresh": "5s",
            "schemaVersion": 41,
            "tags": ["logs", "elasticsearch", f"user-{user_id}"],
            "templating": {
                "list": [
                    {
                        "current": {
                            "text": "All",
                            "value": ["$__all"]
                        },
                        "datasource": {
                            "type": "elasticsearch",
                            "uid": data_source_uid
                        },
                        "definition": "{\"find\": \"terms\", \"field\": \"level\"}",
                        "includeAll": True,
                        "multi": True,
                        "name": "level",
                        "options": [],
                        "query": "{\"find\": \"terms\", \"field\": \"level\"}",
                        "refresh": 1,
                        "regex": "",
                        "type": "query"
                    },
                    {
                        "datasource": {
                            "type": "elasticsearch",
                            "uid": data_source_uid
                        },
                        "filters": [],
                        "label": "Filters",
                        "name": "Filters",
                        "type": "adhoc"
                    }
                ]
            },
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "timepicker": {},
            "timezone": "",
            "title": f"로그 대시보드 - {user_name}",
            "uid": dashboard_uid,
            "version": 1
        }
        
        # 대시보드 생성 API 호출
        return self.create_dashboard(dashboard_data, folder_uid)