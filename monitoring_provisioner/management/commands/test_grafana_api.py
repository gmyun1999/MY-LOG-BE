from django.core.management.base import BaseCommand
import requests
import json


class Command(BaseCommand):
    help = "Test Grafana API capabilities"

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, default="http://localhost:3000",
                            help='Grafana URL')
        parser.add_argument('--api-key', type=str, required=True,
                            help='Grafana Admin API Key')

    def handle(self, *args, **kwargs):
        grafana_url = kwargs['url']
        api_key = kwargs['api_key']
        
        self.stdout.write(f"Testing Grafana API at: {grafana_url}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 1. 기본 연결 테스트
        self.stdout.write("\n1. Testing basic connection...")
        try:
            response = requests.get(f"{grafana_url}/api/health")
            self.stdout.write(self.style.SUCCESS(f"Health check success: {response.json()}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Health check failed: {str(e)}"))
        
        # 2. 버전 정보 확인
        self.stdout.write("\n2. Checking Grafana version...")
        try:
            response = requests.get(f"{grafana_url}/api/frontend/settings", headers=headers)
            if response.status_code == 200:
                settings = response.json()
                version = settings.get("buildInfo", {}).get("version", "Unknown")
                self.stdout.write(self.style.SUCCESS(f"Grafana version: {version}"))
            else:
                self.stdout.write(self.style.WARNING(f"Could not get version: {response.status_code} - {response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Version check failed: {str(e)}"))
        
        # 3. 서비스 계정 API 테스트
        self.stdout.write("\n3. Testing service account API...")
        try:
            # 서비스 계정 검색 API 테스트
            search_response = requests.get(f"{grafana_url}/api/serviceaccounts/search", headers=headers)
            
            if search_response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Service account search API works!"))
                accounts = search_response.json()
                self.stdout.write(f"Found {len(accounts.get('serviceAccounts', []))} service accounts")
                
                # 서비스 계정 생성 테스트
                self.stdout.write("\nTesting service account creation...")
                create_data = {"name": "test-account-api", "role": "Viewer"}
                
                self.stdout.write(f"Request: POST {grafana_url}/api/serviceaccounts")
                self.stdout.write(f"Headers: {json.dumps(headers)}")
                self.stdout.write(f"Data: {json.dumps(create_data)}")
                
                create_response = requests.post(f"{grafana_url}/api/serviceaccounts", 
                                               headers=headers, 
                                               json=create_data)
                
                self.stdout.write(f"Response code: {create_response.status_code}")
                self.stdout.write(f"Response text: {create_response.text}")
                
                if create_response.status_code in [200, 201]:
                    self.stdout.write(self.style.SUCCESS("Service account creation API works!"))
                else:
                    self.stdout.write(self.style.WARNING("Service account creation API failed!"))
                    
                    # Try without role field
                    create_data = {"name": "test-account-api-2"}
                    self.stdout.write("\nTrying without role field...")
                    self.stdout.write(f"Data: {json.dumps(create_data)}")
                    
                    create_response = requests.post(f"{grafana_url}/api/serviceaccounts", 
                                                   headers=headers, 
                                                   json=create_data)
                    
                    self.stdout.write(f"Response code: {create_response.status_code}")
                    self.stdout.write(f"Response text: {create_response.text}")
                    
                    if create_response.status_code in [200, 201]:
                        self.stdout.write(self.style.SUCCESS("Service account creation works without role field!"))
                    else:
                        self.stdout.write(self.style.ERROR("Service account creation API does not work even without role field!"))
            else:
                self.stdout.write(self.style.ERROR(f"Service account search API failed: {search_response.status_code} - {search_response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Service account API test failed: {str(e)}"))
        
        # 4. 폴더 API 테스트
        self.stdout.write("\n4. Testing folder API...")
        try:
            folders_response = requests.get(f"{grafana_url}/api/folders", headers=headers)
            
            if folders_response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Folder API works!"))
                folders = folders_response.json()
                self.stdout.write(f"Found {len(folders)} folders")
                
                # 폴더 생성 테스트
                self.stdout.write("\nTesting folder creation...")
                folder_data = {"title": "Test API Folder"}
                
                folder_response = requests.post(f"{grafana_url}/api/folders", 
                                              headers=headers, 
                                              json=folder_data)
                
                if folder_response.status_code in [200, 201]:
                    self.stdout.write(self.style.SUCCESS("Folder creation API works!"))
                    folder = folder_response.json()
                    folder_uid = folder.get("uid")
                    
                    if folder_uid:
                        # 폴더 권한 설정 테스트
                        self.stdout.write("\nTesting folder permissions API...")
                        perm_data = {
                            "items": [
                                {"role": "Viewer", "permission": 0}
                            ]
                        }
                        
                        perm_response = requests.post(f"{grafana_url}/api/folders/{folder_uid}/permissions", 
                                                     headers=headers, 
                                                     json=perm_data)
                        
                        self.stdout.write(f"Response code: {perm_response.status_code}")
                        self.stdout.write(f"Response text: {perm_response.text}")
                        
                        if perm_response.status_code in [200, 201]:
                            self.stdout.write(self.style.SUCCESS("Folder permissions API works!"))
                        else:
                            self.stdout.write(self.style.ERROR("Folder permissions API failed!"))
                else:
                    self.stdout.write(self.style.ERROR(f"Folder creation API failed: {folder_response.status_code} - {folder_response.text}"))
            else:
                self.stdout.write(self.style.ERROR(f"Folder API failed: {folders_response.status_code} - {folders_response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Folder API test failed: {str(e)}"))
        
        # 5. 대시보드 API 테스트
        self.stdout.write("\n5. Testing dashboard API...")
        try:
            # 간단한 대시보드 생성
            dashboard_data = {
                "dashboard": {
                    "id": None,
                    "title": "Test API Dashboard",
                    "tags": ["test"],
                    "timezone": "browser",
                    "panels": [
                        {
                            "id": 1,
                            "type": "graph",
                            "title": "Test Panel",
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                        }
                    ],
                    "schemaVersion": 16,
                    "version": 0
                },
                "overwrite": True
            }
            
            dashboard_response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                             headers=headers, 
                                             json=dashboard_data)
            
            if dashboard_response.status_code in [200, 201]:
                self.stdout.write(self.style.SUCCESS("Dashboard API works!"))
                result = dashboard_response.json()
                self.stdout.write(f"Created dashboard with URL: {result.get('url')}")
            else:
                self.stdout.write(self.style.ERROR(f"Dashboard API failed: {dashboard_response.status_code} - {dashboard_response.text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Dashboard API test failed: {str(e)}"))
        
        self.stdout.write("\nGrafana API testing completed!")