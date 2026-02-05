"""
Mist API Client
Handles authentication and API requests to Juniper Mist platform
"""

import logging
import requests
import yaml
import time
from typing import Dict, List, Optional
from pathlib import Path


class MistAPIClient:
    """Client for interacting with Juniper Mist API."""
    
    BASE_URL = "https://api.eu.mist.com/api/v1"
    
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
    
    def get_sle_metrics(self, site_id: str, metric: str = None, hours: int = 24) -> Dict:
        """
        Get SLE (Service Level Expectation) metrics for a site.
        
        Args:
            site_id: Site ID
            metric: Optional specific metric to retrieve (e.g., 'time-to-connect', 'throughput', 'capacity')
            hours: Number of hours to look back (default: 24)
        """
        try:
            # Calculate timestamps
            end_time = int(time.time())
            start_time = end_time - (hours * 3600)
            
            # First, get list of available metrics
            metrics_url = f"{self.BASE_URL}/sites/{site_id}/sle/site/{site_id}/metrics"
            response = self.session.get(metrics_url)
            response.raise_for_status()
            available_metrics = response.json()
            
            # If specific metric requested, get its summary
            if metric:
                summary_url = f"{self.BASE_URL}/sites/{site_id}/sle/site/{site_id}/metric/{metric}/summary"
                params = {'start': start_time, 'end': end_time}
                response = self.session.get(summary_url, params=params)
                response.raise_for_status()
                return response.json()
            
            # Otherwise, return available metrics
            return available_metrics
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Failed to get SLE metrics: {e}")
            return None
    
    def get_insights(self, site_id: str = None) -> List[Dict]:
        """
        Get insights for organization or specific site.
        
        For the Mist API, "insights" are actually SLE (Service Level Expectation) metrics
        that measure infrastructure health. These are numeric scores for various metrics.
        
        Args:
            site_id: Optional site ID to filter insights
        
        Returns:
            List of insights/metrics dictionaries converted to insight format
        """
        if not self.org_id:
            raise ValueError("Organization ID not initialized")
        
        try:
            if site_id:
                # Use site-specific insights stats endpoint
                url = f"{self.BASE_URL}/sites/{site_id}/insights/site/{site_id}/stats"
            else:
                # Use organization-level SLE insights endpoint
                url = f"{self.BASE_URL}/orgs/{self.org_id}/insights/sites-sle"
            
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract insights from paginated response
            if isinstance(data, dict) and 'results' in data:
                sle_metrics = data.get('results', [])
                self.logger.info(f"Retrieved {len(sle_metrics)} sites SLE metrics from {data.get('total', 'unknown')} total")
                # Convert SLE metrics to insight format
                insights = self._convert_sle_metrics_to_insights(sle_metrics)
            else:
                # For site-level stats, the entire response is the data
                insights = [data] if data else []
                self.logger.info(f"Retrieved site insights data")
            
            return insights
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get insights: {e}")
            raise
    
    def _convert_sle_metrics_to_insights(self, sle_metrics: List[Dict]) -> List[Dict]:
        """
        Convert SLE metrics to insight format with severity assessment.
        
        Args:
            sle_metrics: List of SLE metric dictionaries
            
        Returns:
            List of insights with assessed severity levels
        """
        insights = []
        
        # Metric thresholds for severity assessment
        thresholds = {
            'critical': 0.70,  # < 70% = critical
            'major': 0.80,     # < 80% = major
            'warning': 0.90    # < 90% = warning
        }
        
        key_metrics = ['capacity', 'roaming', 'successful-connect', 'time-to-connect', 'ap-health']
        
        for site_metric in sle_metrics:
            site_id = site_metric.get('site_id', 'unknown')
            
            # Analyze each key metric for this site
            for metric_name in key_metrics:
                metric_value = site_metric.get(metric_name)
                
                if metric_value is not None:
                    # Determine severity based on threshold
                    severity = 'info'
                    if metric_value < thresholds['critical']:
                        severity = 'critical'
                    elif metric_value < thresholds['major']:
                        severity = 'major'
                    elif metric_value < thresholds['warning']:
                        severity = 'warning'
                    
                    # Create insight from metric
                    insight = {
                        'title': f"{metric_name.replace('-', ' ').title()} Metric",
                        'type': 'sle_metric',
                        'severity': severity,
                        'site_id': site_id,
                        'metric_name': metric_name,
                        'metric_value': round(metric_value, 4),
                        'threshold': thresholds.get(severity, 1.0),
                        'text': f"{metric_name.replace('-', ' ').title()}: {metric_value*100:.1f}% - "
                               f"Site info: {site_metric.get('num_aps', 'N/A')} APs, "
                               f"{site_metric.get('num_clients', 'N/A')} clients"
                    }
                    
                    # Only include non-info insights (or include all for analysis)
                    if severity != 'info':
                        insights.append(insight)
                    elif site_metric.get('num_aps') is not None:  # Include info level with site details
                        insights.append(insight)
        
        return insights
    
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
