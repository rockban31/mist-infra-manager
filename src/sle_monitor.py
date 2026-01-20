"""
SLE Monitor
Monitors Service Level Expectations and proactively identifies issues
"""

import logging
from typing import Dict, List
from datetime import datetime


class SLEMonitor:
    """Monitor and analyze SLE metrics across the infrastructure."""
    
    # SLE thresholds (can be customized)
    THRESHOLDS = {
        'successful_connect': 95.0,  # %
        'time_to_connect': 5.0,       # seconds
        'throughput': 80.0,           # % of expected
        'capacity': 85.0,             # % utilization
        'roaming': 98.0,              # % successful
    }
    
    def __init__(self, mist_client):
        """
        Initialize SLE Monitor.
        
        Args:
            mist_client: MistAPIClient instance
        """
        self.client = mist_client
        self.logger = logging.getLogger(__name__)
    
    def run_monitoring(self):
        """Run SLE monitoring across all sites."""
        self.logger.info("Starting SLE monitoring")
        
        try:
            sites = self.client.get_sites()
            
            for site in sites:
                site_id = site.get('id')
                site_name = site.get('name', 'Unknown')
                
                self.logger.info(f"Monitoring site: {site_name} ({site_id})")
                self._monitor_site(site_id, site_name)
        
        except Exception as e:
            self.logger.error(f"Error during SLE monitoring: {e}")
            raise
    
    def _monitor_site(self, site_id: str, site_name: str):
        """Monitor SLE metrics for a specific site."""
        try:
            # Get available metrics for the site
            try:
                available_metrics = self.client.get_sle_metrics(site_id)
                if available_metrics:
                    supported = available_metrics.get('supported', [])
                    self.logger.debug(f"Site {site_name}: Found {len(supported)} supported SLE metrics")
                else:
                    self.logger.debug(f"Site {site_name}: SLE metrics endpoint not available")
                    return
            except Exception as e:
                self.logger.debug(f"Site {site_name}: SLE metrics not available")
                return
            
            # Common SLE metric names in Mist API
            metrics_to_check = [
                'time-to-connect',
                'successful-connect', 
                'throughput',
                'capacity',
                'roaming'
            ]
            
            issues = []
            
            # Check each metric if available
            for metric in metrics_to_check:
                try:
                    metric_data = self.client.get_sle_metrics(site_id, metric=metric)
                    
                    # Extract value from summary (structure varies by metric)
                    if isinstance(metric_data, dict):
                        # Try to get the current value from different possible locations
                        current_value = None
                        if 'score' in metric_data:
                            current_value = metric_data.get('score')
                        elif 'value' in metric_data:
                            current_value = metric_data.get('value')
                        elif 'summary' in metric_data and isinstance(metric_data['summary'], dict):
                            current_value = metric_data['summary'].get('score') or metric_data['summary'].get('value')
                        
                        if current_value is not None:
                            # Map API metric names to threshold keys
                            threshold_key = metric.replace('-', '_')
                            threshold = self.THRESHOLDS.get(threshold_key)
                            
                            if threshold is not None:
                                issue = self._check_threshold(
                                    metric, 
                                    current_value, 
                                    threshold
                                )
                                if issue:
                                    issues.append(issue)
                                else:
                                    self.logger.info(f"  ✓ {metric}: {current_value:.2f}")
                
                except Exception as e:
                    self.logger.debug(f"  Could not retrieve metric '{metric}': {e}")
            
            # Report findings
            if issues:
                self.logger.warning(
                    f"Site {site_name}: Found {len(issues)} SLE issues"
                )
                for issue in issues:
                    self.logger.warning(f"  ⚠ {issue}")
            else:
                self.logger.info(f"  ✓ Site {site_name}: All SLE metrics within thresholds")
        
        except Exception as e:
            self.logger.error(f"Error monitoring site {site_name}: {e}")
    
    def _check_threshold(
        self, 
        metric_name: str, 
        current_value: float, 
        threshold: float
    ) -> str:
        """
        Check if metric is below threshold.
        
        Returns:
            Issue description if threshold violated, None otherwise
        """
        # For most metrics, lower is worse
        if current_value < threshold:
            return (
                f"{metric_name}: {current_value:.2f} "
                f"(threshold: {threshold:.2f})"
            )
        
        return None
    
    def get_sle_summary(self, site_id: str = None) -> Dict:
        """
        Get summary of SLE metrics.
        
        Args:
            site_id: Optional site ID, if None uses all sites
            
        Returns:
            Dictionary with SLE summary statistics
        """
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'sites_analyzed': 0,
            'total_issues': 0,
            'critical_issues': 0,
            'metrics': {}
        }
        
        try:
            if site_id:
                sites = [{'id': site_id}]
            else:
                sites = self.client.get_sites()
            
            summary['sites_analyzed'] = len(sites)
            
            for site in sites:
                try:
                    sle_data = self.client.get_sle_metrics(site['id'])
                    
                    for metric_name, metric_data in sle_data.items():
                        if isinstance(metric_data, dict):
                            current_value = metric_data.get('value')
                            
                            if metric_name not in summary['metrics']:
                                summary['metrics'][metric_name] = {
                                    'values': [],
                                    'threshold': self.THRESHOLDS.get(metric_name)
                                }
                            
                            if current_value is not None:
                                summary['metrics'][metric_name]['values'].append(
                                    current_value
                                )
                
                except Exception as e:
                    self.logger.error(f"Error getting SLE data for site: {e}")
            
            # Calculate averages
            for metric_name, metric_info in summary['metrics'].items():
                values = metric_info['values']
                if values:
                    metric_info['average'] = sum(values) / len(values)
                    metric_info['min'] = min(values)
                    metric_info['max'] = max(values)
                    
                    # Count issues
                    threshold = metric_info.get('threshold')
                    if threshold:
                        below_threshold = [v for v in values if v < threshold]
                        summary['total_issues'] += len(below_threshold)
        
        except Exception as e:
            self.logger.error(f"Error generating SLE summary: {e}")
        
        return summary
