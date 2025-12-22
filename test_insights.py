from src.mist_client import MistAPIClient
import logging

logging.basicConfig(level=logging.DEBUG)

client = MistAPIClient(config_path='config/config.yaml')
print(f'Org ID: {client.org_id}')
print('\nTrying to get insights...')

try:
    insights = client.get_insights()
    print(f'Success! Got {len(insights)} insights')
    print(f'Insights: {insights}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
    
    # Try alternative endpoints
    print('\nTrying alternative endpoint...')
    import requests
    
    # Try sites endpoint
    try:
        sites = client.get_sites()
        if sites:
            site_id = sites[0]['id']
            print(f'\nTrying with site ID: {site_id}')
            insights = client.get_insights(site_id=site_id)
            print(f'Success with site! Got {len(insights)} insights')
    except Exception as e2:
        print(f'Site-specific error: {type(e2).__name__}: {str(e2)}')
