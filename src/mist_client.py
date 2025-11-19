"""
Mist API Client
Handles authentication and API requests to Juniper Mist platform
"""

import logging
import requests
import yaml
from typing import Dict, List, Optional
from pathlib import Path


class MistAPIClient:
    """Client for interacting with Juniper Mist API."""
    
    BASE_URL = "https://api.mist.com/api/v1"
    
    def __init__(self, config_path: str = None, api_token: str = None):
        """
        Initialize Mist API client.
        
        Args:
            config_path: Path to configuration file
            api_token: API token (overrides config file)
        """
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Load configuration
        if api_token:
            self.api_token = api_token
        elif config_path:
            self._load_config(config_path)
        else:
            raise ValueError("Either config_path or api_token must be provided")
        
        # Set authorization header
        self.session.headers.update({
            'Authorization': f'Token {self.api_token}',
            'Content-Type': 'application/json'
        })
        
        self.org_id = None
        self._initialize_org()
    
    def _load_config(self, config_path: str):
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.api_token = config.get('mist', {}).get('api_token')
        if not self.api_token:
            raise ValueError("API token not found in configuration")
        
        self.logger.info(f"Configuration loaded from {config_path}")
    
    def _initialize_org(self):
        """Get organization ID from the API."""
        try:
            response = self.session.get(f"{self.BASE_URL}/self")
            response.raise_for_status()
            data = response.json()
            
            # Get first organization ID
            privileges = data.get('privileges', [])
            if privileges:
                self.org_id = privileges[0].get('org_id')
                self.logger.info(f"Initialized with organization ID: {self.org_id}")
            else:
                self.logger.warning("No organization privileges found")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to initialize organization: {e}")
            raise
    
    def get_sites(self) -> List[Dict]:
        """Get all sites in the organization."""
        if not self.org_id:
            raise ValueError("Organization ID not initialized")
        
        try:
            response = self.session.get(f"{self.BASE_URL}/orgs/{self.org_id}/sites")
            response.raise_for_status()
            sites = response.json()
            self.logger.info(f"Retrieved {len(sites)} sites")
            return sites
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get sites: {e}")
            raise
    
    def get_devices(self, site_id: str = None) -> List[Dict]:
        """
        Get devices from organization or specific site.
        
        Args:
            site_id: Optional site ID to filter devices
        """
        if not self.org_id:
            raise ValueError("Organization ID not initialized")
        
        try:
            if site_id:
                url = f"{self.BASE_URL}/sites/{site_id}/devices"
            else:
                url = f"{self.BASE_URL}/orgs/{self.org_id}/devices"
            
            response = self.session.get(url)
            response.raise_for_status()
            devices = response.json()
            self.logger.info(f"Retrieved {len(devices)} devices")
            return devices
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get devices: {e}")
            raise
    
    def get_sle_metrics(self, site_id: str, metric: str = None) -> Dict:
        """
        Get SLE (Service Level Expectation) metrics for a site.
        
        Args:
            site_id: Site ID
            metric: Optional specific metric to retrieve
        """
        try:
            url = f"{self.BASE_URL}/sites/{site_id}/sle"
            if metric:
                url += f"/{metric}"
            
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get SLE metrics: {e}")
            raise
    
    def get_insights(self, site_id: str = None) -> List[Dict]:
        """
        Get insights for organization or specific site.
        
        Args:
            site_id: Optional site ID to filter insights
        """
        if not self.org_id:
            raise ValueError("Organization ID not initialized")
        
        try:
            if site_id:
                url = f"{self.BASE_URL}/sites/{site_id}/insights"
            else:
                url = f"{self.BASE_URL}/orgs/{self.org_id}/insights"
            
            response = self.session.get(url)
            response.raise_for_status()
            insights = response.json()
            self.logger.info(f"Retrieved {len(insights)} insights")
            return insights
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get insights: {e}")
            raise
    
    def get_alarms(self, site_id: str = None) -> List[Dict]:
        """
        Get alarms for organization or specific site.
        
        Args:
            site_id: Optional site ID to filter alarms
        """
        if not self.org_id:
            raise ValueError("Organization ID not initialized")
        
        try:
            if site_id:
                url = f"{self.BASE_URL}/sites/{site_id}/alarms"
            else:
                url = f"{self.BASE_URL}/orgs/{self.org_id}/alarms"
            
            response = self.session.get(url)
            response.raise_for_status()
            alarms = response.json()
            self.logger.info(f"Retrieved {len(alarms)} alarms")
            return alarms
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get alarms: {e}")
            raise
