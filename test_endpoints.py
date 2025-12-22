from src.mist_client import MistAPIClient
import logging

logging.basicConfig(level=logging.INFO)

client = MistAPIClient(config_path='config/config.yaml')
print(f'Testing Mist API Endpoints')
print(f'Organization ID: {client.org_id}')
print('=' * 60)

# Test various insights-related endpoints
test_endpoints = [
    f"/orgs/{client.org_id}/insights",
    f"/orgs/{client.org_id}/insights/sites-sle",
    f"/orgs/{client.org_id}/alarms",
    f"/orgs/{client.org_id}/events",
]

for endpoint in test_endpoints:
    url = f"{client.BASE_URL}{endpoint}"
    print(f'\nTesting: {endpoint}')
    try:
        response = client.session.get(url)
        print(f'  Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  [OK] Success! Response type: {type(data)}')
            if isinstance(data, list):
                print(f'  Items count: {len(data)}')
            elif isinstance(data, dict):
                print(f'  Keys: {list(data.keys())}')
        else:
            print(f'  [FAIL] Error: {response.status_code} - {response.reason}')
    except Exception as e:
        print(f'  [ERROR] Exception: {e}')

# Try site-specific insights
print('\n' + '=' * 60)
print('Testing site-specific endpoints:')
sites = client.get_sites()
if sites:
    site = sites[0]
    site_id = site['id']
    site_name = site.get('name', 'Unknown')
    print(f'\nUsing site: {site_name} ({site_id})')
    
    site_endpoints = [
        f"/sites/{site_id}/insights",
        f"/sites/{site_id}/insights/site/{site_id}/stats",
    ]
    
    for endpoint in site_endpoints:
        url = f"{client.BASE_URL}{endpoint}"
        print(f'\nTesting: {endpoint}')
        try:
            response = client.session.get(url)
            print(f'  Status: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'  [OK] Success! Response type: {type(data)}')
                if isinstance(data, list):
                    print(f'  Items count: {len(data)}')
                elif isinstance(data, dict):
                    print(f'  Keys: {list(data.keys())[:10]}')
            else:
                print(f'  [FAIL] Error: {response.status_code} - {response.reason}')
        except Exception as e:
            print(f'  [ERROR] Exception: {e}')
