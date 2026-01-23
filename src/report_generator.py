"""
Report Generator
Generates comprehensive infrastructure reports with summaries, dashboards, and trend analysis
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from trend_analyzer import TrendAnalyzer


class ReportGenerator:
    """Generate comprehensive infrastructure reports."""
    
    def __init__(self, mist_client, trend_analyzer: Optional[TrendAnalyzer] = None):
        """
        Initialize Report Generator.
        
        Args:
            mist_client: MistAPIClient instance
            trend_analyzer: Optional TrendAnalyzer instance for trend analysis
        """
        self.client = mist_client
        self.logger = logging.getLogger(__name__)
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        self.trend_analyzer = trend_analyzer
    
    def generate_report(self):
        """Generate complete infrastructure report."""
        self.logger.info("="*60)
        self.logger.info("INFRASTRUCTURE REPORT GENERATION")
        self.logger.info("="*60)
        
        try:
            # Gather data
            sites = self._get_sites_data()
            insights = self._get_insights_data()
            health_status = self._calculate_health_status(sites, insights)
            
            # Generate reports
            self._generate_summary_report(sites, insights, health_status)
            self._generate_health_dashboard(health_status, sites)
            health_dashboard_json = self._generate_health_dashboard_json(health_status, sites)
            
            # Analyze trends if trend analyzer is available
            trend_report_text = ""
            trends = None
            if self.trend_analyzer:
                trends = self.trend_analyzer.analyze_trends(health_dashboard_json)
                trend_report_text = self.trend_analyzer.generate_trend_report(
                    health_dashboard_json, trends
                )
                # Save current report to history
                self.trend_analyzer.save_report_to_history(health_dashboard_json)
                # Log trend information
                self.logger.info(trend_report_text)
            
            # Return trend data for notifications
            return {
                'health_status': health_status,
                'trends': trends,
                'health_dashboard_json': health_dashboard_json
            }
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
            raise
    
    def _get_sites_data(self) -> List[Dict]:
        """Retrieve all sites data."""
        try:
            sites = self.client.get_sites()
            self.logger.debug(f"Retrieved data for {len(sites)} sites")
            return sites
        except Exception as e:
            self.logger.warning(f"Could not retrieve sites data: {e}")
            return []
    
    def _get_insights_data(self) -> List[Dict]:
        """Retrieve all insights data."""
        try:
            insights = self.client.get_insights()
            self.logger.debug(f"Retrieved {len(insights)} insights")
            return insights
        except Exception as e:
            self.logger.warning(f"Could not retrieve insights data: {e}")
            return []
    
    def _calculate_health_status(self, sites: List[Dict], insights: List[Dict]) -> Dict:
        """Calculate overall infrastructure health status."""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'total_sites': len(sites),
            'critical_insights': 0,
            'major_insights': 0,
            'warning_insights': 0,
            'info_insights': 0,
            'overall_health': 'UNKNOWN',
            'sites_status': {}
        }
        
        # Count insights by severity
        for insight in insights:
            severity = insight.get('severity', 'unknown').lower()
            if severity == 'critical':
                health_status['critical_insights'] += 1
            elif severity == 'major':
                health_status['major_insights'] += 1
            elif severity == 'warning':
                health_status['warning_insights'] += 1
            elif severity == 'info':
                health_status['info_insights'] += 1
        
        # Determine overall health
        if health_status['critical_insights'] > 0:
            health_status['overall_health'] = 'CRITICAL'
        elif health_status['major_insights'] > 0:
            health_status['overall_health'] = 'UNHEALTHY'
        elif health_status['warning_insights'] > 0:
            health_status['overall_health'] = 'DEGRADED'
        else:
            health_status['overall_health'] = 'HEALTHY'
        
        # Site status breakdown
        for site in sites:
            site_id = site.get('id')
            site_name = site.get('name', 'Unknown')
            site_insights = [i for i in insights if i.get('site_id') == site_id]
            
            site_severity = 'HEALTHY'
            if any(i.get('severity', '').lower() == 'critical' for i in site_insights):
                site_severity = 'CRITICAL'
            elif any(i.get('severity', '').lower() == 'major' for i in site_insights):
                site_severity = 'UNHEALTHY'
            elif any(i.get('severity', '').lower() == 'warning' for i in site_insights):
                site_severity = 'DEGRADED'
            
            health_status['sites_status'][site_name] = {
                'id': site_id,
                'status': site_severity,
                'insight_count': len(site_insights)
            }
        
        return health_status
    
    def _sort_insights_by_priority(self, insights: List[Dict]) -> Dict[str, List[Dict]]:
        """Sort insights by priority (severity) level."""
        severity_priority = {
            'critical': 0,
            'major': 1,
            'warning': 2,
            'info': 3
        }
        
        sorted_by_priority = {
            'critical': [],
            'major': [],
            'warning': [],
            'info': []
        }
        
        for insight in insights:
            severity = insight.get('severity', 'info').lower()
            if severity in sorted_by_priority:
                sorted_by_priority[severity].append(insight)
        
        # Sort within each priority level
        for severity in sorted_by_priority:
            sorted_by_priority[severity].sort(key=lambda x: x.get('title', ''))
        
        return sorted_by_priority
    
    def _get_priority_action_text(self, severity: str) -> str:
        """Get action recommendations based on severity level."""
        action_map = {
            'critical': 'URGENT - Immediate action required',
            'major': 'HIGH - Address within 24 hours',
            'warning': 'MEDIUM - Monitor closely',
            'info': 'INFO - Normal operation'
        }
        return action_map.get(severity.lower(), 'Unknown')
    
    def _generate_summary_report(self, sites: List[Dict], insights: List[Dict], health_status: Dict):
        """Generate summary report with priority-sorted insights."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_name = f"SUMMARY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = self.report_dir / report_name
        
        # Create site ID to name mapping
        site_id_to_name = {site.get('id'): site.get('name', 'Unknown') for site in sites}
        
        # Sort insights by priority
        sorted_insights = self._sort_insights_by_priority(insights)
        
        with open(report_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("MIST INFRASTRUCTURE SUMMARY REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Report Generated: {timestamp}\n")
            f.write(f"Organization ID: {self.client.org_id}\n\n")
            
            # Overall Health
            f.write("OVERALL INFRASTRUCTURE HEALTH\n")
            f.write("-" * 70 + "\n")
            f.write(f"Status: {health_status['overall_health']}\n")
            f.write(f"Total Sites: {health_status['total_sites']}\n")
            f.write(f"Total Insights: {len(insights)}\n\n")
            
            # Insights Breakdown
            f.write("INSIGHTS BREAKDOWN (BY PRIORITY)\n")
            f.write("-" * 70 + "\n")
            f.write(f"  [CRIT] Critical: {health_status['critical_insights']} - {self._get_priority_action_text('critical')}\n")
            f.write(f"  [FAIL] Major:    {health_status['major_insights']} - {self._get_priority_action_text('major')}\n")
            f.write(f"  [WARN] Warning:  {health_status['warning_insights']} - {self._get_priority_action_text('warning')}\n")
            f.write(f"  [INFO] Info:     {health_status['info_insights']} - {self._get_priority_action_text('info')}\n\n")
            
            # Sites Status
            f.write("SITES STATUS\n")
            f.write("-" * 70 + "\n")
            for site_name, site_info in health_status['sites_status'].items():
                f.write(f"  {site_name:30} | Status: {site_info['status']:10} | ")
                f.write(f"Insights: {site_info['insight_count']}\n")
            
            f.write("\n")
            f.write("DETAILED INSIGHTS (PRIORITY-SORTED)\n")
            f.write("-" * 70 + "\n")
            
            if insights:
                counter = 1
                # Display critical alerts first
                for severity in ['critical', 'major', 'warning', 'info']:
                    severity_insights = sorted_insights[severity]
                    if severity_insights:
                        f.write(f"\n[{severity.upper()}] {self._get_priority_action_text(severity)}\n")
                        f.write("-" * 70 + "\n")
                        for insight in severity_insights:
                            f.write(f"\n{counter}. {insight.get('title', 'Unknown Insight')}\n")
                            f.write(f"   Severity: {insight.get('severity', 'unknown')}\n")
                            f.write(f"   Type: {insight.get('type', 'unknown')}\n")
                            if 'site_id' in insight:
                                site_name = site_id_to_name.get(insight['site_id'], 'Unknown')
                                f.write(f"   Site: {site_name}\n")
                                f.write(f"   Site ID: {insight['site_id']}\n")
                            if 'text' in insight:
                                f.write(f"   Details: {insight['text']}\n")
                            counter += 1
            else:
                f.write("No insights available.\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("End of Report\n")
            f.write("=" * 70 + "\n")
        
        self.logger.info(f"Summary Report generated: {report_name}")
    
    def _generate_health_dashboard(self, health_status: Dict, sites: List[Dict]):
        """Generate health dashboard with action recommendations."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dashboard_name = f"HEALTH_DASHBOARD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        dashboard_path = self.report_dir / dashboard_name
        
        # Status symbols
        status_symbols = {
            'HEALTHY': '[OK] HEALTHY',
            'DEGRADED': '[WARN] DEGRADED',
            'UNHEALTHY': '[FAIL] UNHEALTHY',
            'CRITICAL': '[CRIT] CRITICAL'
        }
        
        with open(dashboard_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("INFRASTRUCTURE HEALTH DASHBOARD\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Overall Status: {status_symbols.get(health_status['overall_health'], health_status['overall_health'])}\n\n")
            
            # Priority-based action recommendations
            f.write("ACTION RECOMMENDATIONS (BY PRIORITY)\n")
            f.write("-" * 70 + "\n")
            
            if health_status['critical_insights'] > 0:
                f.write(f"[CRIT] CRITICAL ({health_status['critical_insights']} issues)\n")
                f.write(f"       {self._get_priority_action_text('critical')}\n")
                f.write("       - Investigate immediately\n")
                f.write("       - Engage incident response team\n")
                f.write("       - Estimate resolution time\n\n")
            
            if health_status['major_insights'] > 0:
                f.write(f"[FAIL] MAJOR ({health_status['major_insights']} issues)\n")
                f.write(f"       {self._get_priority_action_text('major')}\n")
                f.write("       - Create tickets for remediation\n")
                f.write("       - Schedule maintenance window\n")
                f.write("       - Document impact and workarounds\n\n")
            
            if health_status['warning_insights'] > 0:
                f.write(f"[WARN] WARNING ({health_status['warning_insights']} issues)\n")
                f.write(f"       {self._get_priority_action_text('warning')}\n")
                f.write("       - Monitor trending metrics\n")
                f.write("       - Plan preventive maintenance\n")
                f.write("       - Update runbooks if applicable\n\n")
            
            if health_status['info_insights'] > 0 and (health_status['critical_insights'] == 0 and 
                                                        health_status['major_insights'] == 0 and 
                                                        health_status['warning_insights'] == 0):
                f.write(f"[INFO] All systems normal\n")
                f.write("       Continue routine monitoring\n\n")
            
            # Summary statistics
            f.write("HEALTH STATISTICS\n")
            f.write("-" * 70 + "\n")
            total_issues = (health_status['critical_insights'] + 
                          health_status['major_insights'] + 
                          health_status['warning_insights'])
            
            f.write(f"Total Issues:    {total_issues}\n")
            f.write(f"  [CRIT] Critical:   {health_status['critical_insights']}\n")
            f.write(f"  [WARN] Major:      {health_status['major_insights']}\n")
            f.write(f"  [!] Warning:       {health_status['warning_insights']}\n")
            f.write(f"  [i] Info:          {health_status['info_insights']}\n\n")
            
            # Site status grid
            f.write("SITE STATUS GRID\n")
            f.write("-" * 70 + "\n")
            
            healthy_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'HEALTHY')
            degraded_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'DEGRADED')
            unhealthy_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'UNHEALTHY')
            critical_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'CRITICAL')
            
            f.write(f"Healthy:    {healthy_sites}\n")
            f.write(f"Degraded:   {degraded_sites}\n")
            f.write(f"Unhealthy:  {unhealthy_sites}\n")
            f.write(f"Critical:   {critical_sites}\n\n")
            
            # Individual site status - sorted by severity (critical sites first)
            f.write("INDIVIDUAL SITE STATUS (PRIORITY-ORDERED)\n")
            f.write("-" * 70 + "\n")
            f.write(f"{'Site Name':<30} | {'Status':<12} | Insights\n")
            f.write("-" * 70 + "\n")
            
            # Sort sites by severity for display
            severity_order = {'CRITICAL': 0, 'UNHEALTHY': 1, 'DEGRADED': 2, 'HEALTHY': 3}
            sorted_sites = sorted(health_status['sites_status'].items(), 
                                key=lambda x: severity_order.get(x[1]['status'], 4))
            
            for site_name, site_info in sorted_sites:
                status = site_info['status']
                symbol = status_symbols.get(status, status)
                f.write(f"{site_name:<30} | {symbol:<12} | {site_info['insight_count']}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("Dashboard generated successfully\n")
            f.write("=" * 70 + "\n")
        
        self.logger.info(f"Health Dashboard generated: {dashboard_name}")
    
    def _generate_health_dashboard_json(self, health_status: Dict, sites: List[Dict]):
        """Generate health dashboard in JSON format."""
        json_name = f"HEALTH_DASHBOARD_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.report_dir / json_name
        
        # Create JSON structure
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'organization_id': self.client.org_id,
            'overall_status': health_status['overall_health'],
            'total_sites': health_status['total_sites'],
            'health_summary': {
                'critical': health_status['critical_insights'],
                'major': health_status['major_insights'],
                'warning': health_status['warning_insights'],
                'info': health_status['info_insights']
            },
            'sites': health_status['sites_status']
        }
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        self.logger.info(f"Health Dashboard JSON generated: {json_name}")
        return json_data
