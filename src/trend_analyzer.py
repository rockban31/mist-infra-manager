"""
Trend Analyzer
Compares historical metrics and detects trends/degradation
"""

import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TrendAnalyzer:
    """Analyze trends in infrastructure metrics."""
    
    def __init__(self, history_dir: str = "reports/history", keep_days: int = 7):
        """
        Initialize Trend Analyzer.
        
        Args:
            history_dir: Directory to store historical reports
            keep_days: Number of days to keep in history
        """
        self.logger = logging.getLogger(__name__)
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.keep_days = keep_days
    
    def save_report_to_history(self, report_data: Dict, report_type: str = "HEALTH_DASHBOARD"):
        """
        Save current report to history.
        
        Args:
            report_data: Report data to save
            report_type: Type of report (HEALTH_DASHBOARD, SUMMARY_REPORT, etc.)
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            today_dir = self.history_dir / today
            today_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = today_dir / f"{report_type}_{timestamp}.json"
            
            # Save as JSON
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved report to history: {filename}")
            
            # Cleanup old reports
            self._cleanup_old_reports()
            
        except Exception as e:
            self.logger.error(f"Error saving report to history: {e}")
    
    def get_previous_report(self, days_ago: int = 1) -> Optional[Dict]:
        """
        Get the most recent report from N days ago.
        
        Args:
            days_ago: Number of days to look back
            
        Returns:
            Report data or None if not found
        """
        try:
            target_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            target_dir = self.history_dir / target_date
            
            if not target_dir.exists():
                self.logger.debug(f"No reports found for {target_date}")
                return None
            
            # Get the most recent report from that day
            json_files = sorted(target_dir.glob("HEALTH_DASHBOARD_*.json"), reverse=True)
            
            if json_files:
                with open(json_files[0], 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving previous report: {e}")
            return None
    
    def analyze_trends(self, current_report: Dict) -> Dict:
        """
        Analyze trends by comparing with previous day's report.
        
        Args:
            current_report: Current health report
            
        Returns:
            Trend analysis results
        """
        previous_report = self.get_previous_report(days_ago=1)
        
        trends = {
            'timestamp': datetime.now().isoformat(),
            'has_previous_data': previous_report is not None,
            'metrics_trend': {},
            'overall_trend': '→',  # Default: stable
            'degradation_alerts': [],
            'improvement_alerts': []
        }
        
        if not previous_report:
            self.logger.debug("No previous report found for trend analysis")
            return trends
        
        # Extract key metrics
        current_metrics = self._extract_metrics(current_report)
        previous_metrics = self._extract_metrics(previous_report)
        
        # Calculate trends
        for metric_name, current_value in current_metrics.items():
            if metric_name in previous_metrics:
                previous_value = previous_metrics[metric_name]
                trend_data = self._calculate_metric_trend(
                    metric_name, previous_value, current_value
                )
                trends['metrics_trend'][metric_name] = trend_data
                
                # Check for degradation
                if trend_data['is_degrading']:
                    trends['degradation_alerts'].append({
                        'metric': metric_name,
                        'previous': previous_value,
                        'current': current_value,
                        'change_percent': trend_data['change_percent'],
                        'indicator': trend_data['indicator']
                    })
        
        # Determine overall trend
        if trends['degradation_alerts']:
            trends['overall_trend'] = 'UP'  # Worsening
        elif trends['improvement_alerts']:
            trends['overall_trend'] = 'DOWN'  # Improving
        else:
            trends['overall_trend'] = '-'  # Stable
        
        return trends
    
    def _extract_metrics(self, report: Dict) -> Dict:
        """Extract key metrics from report."""
        metrics = {}
        
        try:
            # Extract insights counts
            metrics['critical_insights'] = report.get('critical_insights', 0)
            metrics['major_insights'] = report.get('major_insights', 0)
            metrics['warning_insights'] = report.get('warning_insights', 0)
            
            # Extract site-level metrics if available
            sites_status = report.get('sites_status', {})
            for site_name, site_data in sites_status.items():
                if isinstance(site_data, dict):
                    for key in ['capacity', 'roaming', 'successful_connect', 'time_to_connect']:
                        if key in site_data:
                            metric_key = f"{site_name}_{key}"
                            metrics[metric_key] = site_data[key]
            
        except Exception as e:
            self.logger.warning(f"Error extracting metrics: {e}")
        
        return metrics
    
    def _calculate_metric_trend(self, metric_name: str, previous_value: float, 
                                current_value: float) -> Dict:
        """Calculate trend for a specific metric."""
        trend = {
            'metric': metric_name,
            'previous_value': previous_value,
            'current_value': current_value,
            'is_degrading': False,
            'indicator': '-',
            'change_percent': 0.0
        }
        
        try:
            if isinstance(previous_value, (int, float)) and isinstance(current_value, (int, float)):
                if previous_value != 0:
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                else:
                    change_percent = 0 if current_value == previous_value else 100
                
                trend['change_percent'] = round(change_percent, 2)
                
                # Determine if degrading (context-dependent)
                if metric_name.endswith('_insights') or metric_name.endswith('_connect'):
                    # For insights and errors: higher is worse
                    if current_value > previous_value:
                        trend['is_degrading'] = True
                        trend['indicator'] = 'UP'
                    elif current_value < previous_value:
                        trend['indicator'] = 'DOWN'
                else:
                    # For capacities/utilization: higher is worse
                    if current_value > previous_value:
                        trend['is_degrading'] = True
                        trend['indicator'] = 'UP'
                    elif current_value < previous_value:
                        trend['indicator'] = 'DOWN'
        
        except Exception as e:
            self.logger.debug(f"Error calculating trend for {metric_name}: {e}")
        
        return trend
    
    def generate_trend_report(self, current_report: Dict, trends: Dict) -> str:
        """
        Generate human-readable trend report.
        
        Args:
            current_report: Current health report
            trends: Trend analysis results
            
        Returns:
            Formatted trend report string
        """
        report_lines = []
        report_lines.append("\n" + "="*70)
        report_lines.append("TREND ANALYSIS REPORT")
        report_lines.append("="*70)
        
        if not trends['has_previous_data']:
            report_lines.append("\n[WARNING] No historical data available for trend analysis")
            report_lines.append("Trends will be available after next report generation")
            return "\n".join(report_lines)
        
        # Overall trend
        trend_symbol = trends['overall_trend']
        if trend_symbol == '→':
            trend_symbol = '[STABLE]'
        elif trend_symbol == '↑':
            trend_symbol = '[WORSENING]'
        elif trend_symbol == '↓':
            trend_symbol = '[IMPROVING]'
        report_lines.append(f"\nOverall Trend: {trend_symbol}")
        
        # Degradation alerts
        if trends['degradation_alerts']:
            report_lines.append("\n[DEGRADATION] Degradation Detected:")
            for alert in trends['degradation_alerts']:
                report_lines.append(
                    f"  - {alert['metric']}: {alert['previous']:.1f} -> {alert['current']:.1f} "
                    f"({alert['change_percent']:+.1f}%) {alert['indicator']}"
                )
        
        # Improvement alerts
        if trends['improvement_alerts']:
            report_lines.append("\n[IMPROVEMENT] Improvements Detected:")
            for alert in trends['improvement_alerts']:
                report_lines.append(
                    f"  - {alert['metric']}: {alert['previous']:.1f} -> {alert['current']:.1f} "
                    f"({alert['change_percent']:+.1f}%) {alert['indicator']}"
                )
        
        # Stable metrics
        stable_metrics = [
            m for m in trends['metrics_trend'].values() 
            if m['indicator'] == '-'
        ]
        if stable_metrics:
            report_lines.append(f"\n[STABLE] {len(stable_metrics)} metric(s) stable")
        
        report_lines.append("\n" + "="*70 + "\n")
        
        return "\n".join(report_lines)
    
    def _cleanup_old_reports(self):
        """Remove reports older than keep_days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.keep_days)
            
            for date_dir in self.history_dir.iterdir():
                if date_dir.is_dir():
                    try:
                        dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                        if dir_date < cutoff_date:
                            import shutil
                            shutil.rmtree(date_dir)
                            self.logger.info(f"Removed old report directory: {date_dir.name}")
                    except ValueError:
                        # Skip directories that don't match date format
                        pass
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old reports: {e}")
    
    def get_history_summary(self) -> Dict:
        """Get summary of stored history."""
        try:
            summary = {
                'total_days': 0,
                'date_range': None,
                'report_count': 0,
                'dates': []
            }
            
            if self.history_dir.exists():
                date_dirs = sorted([d for d in self.history_dir.iterdir() if d.is_dir()])
                summary['total_days'] = len(date_dirs)
                summary['dates'] = [d.name for d in date_dirs]
                
                if date_dirs:
                    summary['date_range'] = f"{date_dirs[0].name} to {date_dirs[-1].name}"
                
                # Count all reports
                for date_dir in date_dirs:
                    summary['report_count'] += len(list(date_dir.glob("*.json")))
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Error getting history summary: {e}")
            return {}
