"""
Report Generator
Generates comprehensive infrastructure reports with summaries, dashboards, and trend analysis
"""

import logging
import json
import html
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from trend_analyzer import TrendAnalyzer

# Mapping of SLE metric names to their expected classifiers (ordered)
# Names sourced from Mist EU API /metric/{metric}/summary endpoint
SLE_CLASSIFIER_MAP = {
    'time-to-connect': [
        'association', 'authorization', 'dhcp-nack', 'dhcp-stuck',
        'dhcp-unresponsive', 'IP-Services',
    ],
    'successful-connect': [
        'association', 'authorization', 'dns', 'dhcp-incomplete',
        'dhcp-nack', 'dhcp-discover-unresponsive', 'dhcp-renew-unresponsive', 'arp',
    ],
    'coverage': [
        'weak-signal', 'asymmetry-downlink', 'asymmetry-uplink',
    ],
    'roaming': [
        'latency-slow-standard-roam', 'latency-slow-11r-roam', 'latency-slow-okc-roam',
        'stability-failed-to-fast-roam', 'signal-quality-suboptimal-roam',
        'signal-quality-sticky-client', 'signal-quality-interband-roam',
    ],
    'throughput': [
        'network-issues', 'coverage', 'device-capability',
        'capacity-non-wifi-interference', 'capacity-wifi-interference',
        'capacity-excessive-client-load', 'capacity-high-bandwidth-utilization',
    ],
    'capacity': [
        'non-wifi-interference', 'wifi-interference', 'client-usage', 'client-count',
    ],
    'ap-health': [
        'low-power', 'ap-disconnected-ap-reboot', 'ap-disconnected-ap-unreachable',
        'ap-disconnected-switch-down', 'ap-disconnected-site-down',
        'ethernet-ethernet-errors', 'ethernet-speed-mismatch',
        'network-jitter', 'network-latency', 'network-tunnel-down',
    ],
}

# Human-friendly display names for SLE metrics
SLE_DISPLAY_NAMES = {
    'time-to-connect': 'Time to Connect',
    'successful-connect': 'Successful Connects',
    'coverage': 'Coverage',
    'roaming': 'Roaming',
    'throughput': 'Throughput',
    'capacity': 'Capacity',
    'ap-health': 'AP Health',
}

# Mapping from org-level insight metric names to SLE summary endpoint names
# The org-level insights API uses "successful-connect" but the per-site
# SLE summary endpoint uses "failed-to-connect"
SLE_ENDPOINT_MAP = {
    'successful-connect': 'failed-to-connect',
}


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
    
    def _dbm_to_quality_percentage(self, dbm_value):
        """
        Convert WiFi signal strength (dBm) to quality percentage.
        
        dBm scale (signal strength):
        -30 to -50 dBm = Excellent (95-100%)
        -50 to -60 dBm = Good (85-95%)
        -60 to -70 dBm = Fair (70-85%)
        -70 to -80 dBm = Weak (50-70%)
        Below -80 dBm = Very Poor (0-50%)
        
        Args:
            dbm_value: Signal strength in dBm (negative value)
            
        Returns:
            Quality percentage (0-100)
        """
        if dbm_value >= -50:
            # Excellent: -30 to -50 dBm maps to 95-100%
            return 95 + (dbm_value + 50) * (5 / 20)
        elif dbm_value >= -60:
            # Good: -50 to -60 dBm maps to 85-95%
            return 85 + (dbm_value + 60) * (10 / 10)
        elif dbm_value >= -70:
            # Fair: -60 to -70 dBm maps to 70-85%
            return 70 + (dbm_value + 70) * (15 / 10)
        elif dbm_value >= -80:
            # Weak: -70 to -80 dBm maps to 50-70%
            return 50 + (dbm_value + 80) * (20 / 10)
        else:
            # Very Poor: below -80 dBm maps to 0-50%
            return max(0, 50 + (dbm_value + 80) * (50 / 20))
    
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
            summary_report_path = self._generate_summary_report(sites, insights, health_status)
            dashboard_content = self._generate_health_dashboard(health_status, sites)
            health_dashboard_json = self._generate_health_dashboard_json(health_status, sites)
            insights_table_html = self._build_grouped_insights_tables_html(insights, sites)
            
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
            
            # Return trend data for notifications with dashboard content and attachment
            return {
                'health_status': health_status,
                'trends': trends,
                'health_dashboard_json': health_dashboard_json,
                'dashboard_content': dashboard_content,
                'report_text': dashboard_content,
                'summary_report_path': summary_report_path,
                'insights_table_html': insights_table_html
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
        """Retrieve all insights data including throughput and coverage with classifier enrichment."""
        try:
            # Get standard insights from Insights API
            insights = self.client.get_insights()
            self.logger.debug(f"Retrieved {len(insights)} standard insights")
            
            # Get additional SLE metrics (throughput and coverage) for each site
            sites = self.client.get_sites()
            additional_metrics = ['throughput', 'coverage']
            
            # Cache for SLE summary API responses: (site_id, metric_name) -> response
            sle_summary_cache = {}
            
            for site in sites:
                site_id = site.get('id')
                site_name = site.get('name', 'Unknown')
                
                for metric_name in additional_metrics:
                    try:
                        metric_data = self.client.get_sle_metrics(site_id, metric=metric_name)
                        if metric_data and 'sle' in metric_data:
                            # Cache the full response for classifier extraction later
                            sle_summary_cache[(site_id, metric_name)] = metric_data
                            
                            # SLE data structure has nested samples
                            sle_dict = metric_data.get('sle', {})
                            
                            # Check if this is the new structure with samples
                            if 'samples' in sle_dict and 'value' in sle_dict['samples']:
                                values = sle_dict['samples']['value']
                                if values:
                                    # Check if metric uses dBm (signal strength) units
                                    y_label = sle_dict.get('y_label', '')
                                    original_dbm_value = None
                                    
                                    if y_label == 'dBm':
                                        # Store original dBm average for display
                                        original_dbm_value = sum(values) / len(values)
                                        # Convert dBm values to quality percentages
                                        quality_values = [self._dbm_to_quality_percentage(v) for v in values]
                                        avg_score = sum(quality_values) / len(quality_values)
                                        self.logger.debug(f"Converted {metric_name} from dBm ({original_dbm_value:.1f}) to quality: avg {avg_score:.1f}%")
                                    else:
                                        # Calculate average from all values as-is
                                        avg_score = sum(values) / len(values)

                                    
                                    # Determine severity based on threshold
                                    severity = 'info'
                                    if avg_score < 70.0:
                                        severity = 'critical'
                                    elif avg_score < 80.0:
                                        severity = 'major'
                                    elif avg_score < 90.0:
                                        severity = 'warning'
                                    
                                    # Create insight text with dBm value if available
                                    if original_dbm_value is not None:
                                        metric_text = f"{metric_name.capitalize()}: {original_dbm_value:.1f} dBm ({avg_score:.1f}%) - Site: {site_name}"
                                    else:
                                        metric_text = f"{metric_name.capitalize()}: {avg_score:.1f}% - Site: {site_name}"
                                    
                                    # Create insight from metric
                                    insight = {
                                        'title': f"{metric_name.capitalize()} Metric",
                                        'type': 'sle_metric',
                                        'severity': severity,
                                        'site_id': site_id,
                                        'metric_name': metric_name,
                                        'metric_value': avg_score / 100.0,  # Convert to 0-1 range
                                        'text': metric_text
                                    }
                                    insights.append(insight)
                                    self.logger.debug(f"Added {metric_name} metric for {site_name}: {avg_score:.1f}%")
                    
                    except Exception as e:
                        self.logger.debug(f"Could not retrieve {metric_name} for site {site_name}: {e}")
            
            # Enrich ALL sle_metric insights with structured classifier data
            # Fetch SLE summaries for org-level metrics that weren't fetched above
            classifier_cache = {}
            for insight in insights:
                if insight.get('type') == 'sle_metric':
                    site_id = insight.get('site_id')
                    metric_name = insight.get('metric_name')
                    if site_id and metric_name:
                        cache_key = (site_id, metric_name)
                        if cache_key not in classifier_cache:
                            # Use cached summary response if available, otherwise fetch
                            cached_response = sle_summary_cache.get(cache_key)
                            if not cached_response:
                                # Map metric name to correct SLE endpoint name
                                api_metric = SLE_ENDPOINT_MAP.get(metric_name, metric_name)
                                cached_response = self.client.get_sle_metrics(site_id, metric=api_metric)
                                if cached_response:
                                    sle_summary_cache[cache_key] = cached_response
                            classifier_cache[cache_key] = self._extract_classifier_data(
                                metric_name, cached_response
                            )
                        insight['classifier_data'] = classifier_cache[cache_key]

            self.logger.info(f"Retrieved {len(insights)} total insights (including throughput/coverage)")
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

    def _extract_classifier_data(self, metric_name: str, summary_response: Optional[Dict] = None) -> Dict[str, Dict]:
        """
        Extract structured classifier data from SLE metric summary response.
        
        Args:
            metric_name: SLE metric name (e.g., 'capacity', 'roaming')
            summary_response: Cached API response (avoids redundant API call)
            
        Returns:
            Dict keyed by classifier name with percent_degraded, num_users, num_aps
        """
        result = {}
        try:
            classifiers = summary_response.get('classifiers', []) if summary_response else []
            expected = SLE_CLASSIFIER_MAP.get(metric_name, [])
            
            if not classifiers:
                if expected:
                    self.logger.debug(f"No classifiers returned for {metric_name} (expected: {expected})")
                return result

            for classifier in classifiers:
                name = classifier.get('name', 'unknown')
                samples = classifier.get('samples', {})
                degraded = samples.get('degraded', []) or []
                total = samples.get('total', []) or []
                degraded_sum = float(sum(d for d in degraded if d is not None)) if degraded else 0.0
                total_sum = float(sum(t for t in total if t is not None)) if total else 0.0
                percent = (degraded_sum / total_sum * 100.0) if total_sum else 0.0
                impact = classifier.get('impact', {})
                
                result[name] = {
                    'percent_degraded': round(percent, 1),
                    'num_users': impact.get('num_users'),
                    'num_aps': impact.get('num_aps'),
                }

            # Log missing expected classifiers
            found = set(result.keys())
            expected_set = set(expected)
            missing = expected_set - found
            extra = found - expected_set
            if missing:
                self.logger.debug(f"{metric_name}: missing expected classifiers: {missing}")
            if extra:
                self.logger.debug(f"{metric_name}: unexpected classifiers from API: {extra}")

        except Exception as e:
            self.logger.debug(f"Could not extract classifier data for {metric_name}: {e}")
        
        return result

    def _build_grouped_insights_tables_html(self, insights: List[Dict], sites: List[Dict]) -> str:
        """
        Build grouped HTML tables — one per SLE metric — with classifier sub-columns.
        
        Each table has columns: Priority | Site | Score | [classifier1] | [classifier2] | ...
        Classifier values show: X.X% degraded, users=N, aps=N
        """
        if not insights:
            return ""

        site_id_to_name = {site.get('id'): site.get('name', 'Unknown') for site in sites}
        
        # Group insights by metric_name
        metric_groups = {}
        for insight in insights:
            if insight.get('type') != 'sle_metric':
                continue
            metric_name = insight.get('metric_name', 'unknown')
            metric_groups.setdefault(metric_name, []).append(insight)
        
        if not metric_groups:
            return ""

        # Determine display order: sort metric groups by highest severity first
        severity_rank = {'critical': 0, 'major': 1, 'warning': 2, 'info': 3}
        
        def group_sort_key(metric_name):
            group_insights = metric_groups[metric_name]
            min_sev = min(severity_rank.get(i.get('severity', 'info'), 3) for i in group_insights)
            return (min_sev, metric_name)
        
        sorted_metrics = sorted(metric_groups.keys(), key=group_sort_key)
        
        # Severity badge colors for inline styling
        severity_colors = {
            'critical': '#d32f2f',
            'major': '#e65100',
            'warning': '#f57c00',
            'info': '#388e3c',
        }
        
        tables_html = []
        for metric_name in sorted_metrics:
            group_insights = metric_groups[metric_name]
            display_name = SLE_DISPLAY_NAMES.get(metric_name, metric_name.replace('-', ' ').title())
            expected_classifiers = SLE_CLASSIFIER_MAP.get(metric_name, [])
            
            # If no classifier map entry, discover classifiers from data
            if not expected_classifiers:
                all_classifier_names = set()
                for ins in group_insights:
                    cd = ins.get('classifier_data', {})
                    all_classifier_names.update(cd.keys())
                expected_classifiers = sorted(all_classifier_names)
            
            # Build classifier column headers (title-case, hyphens to spaces)
            classifier_headers = []
            for c in expected_classifiers:
                classifier_headers.append(c.replace('-', ' ').title())
            
            # Build header row
            header_cols = "<th>Priority</th><th>Site</th><th>Score</th>"
            for ch in classifier_headers:
                header_cols += f"<th>{html.escape(ch)}</th>"
            
            # Sort insights within group by severity then site name
            group_insights.sort(key=lambda i: (
                severity_rank.get(i.get('severity', 'info'), 3),
                site_id_to_name.get(i.get('site_id', ''), 'ZZZ')
            ))
            
            # Build rows
            rows = []
            for insight in group_insights:
                severity = insight.get('severity', 'info').lower()
                priority_label = severity.upper()
                sev_color = severity_colors.get(severity, '#333')
                site_id = insight.get('site_id')
                site_name = site_id_to_name.get(site_id, 'Org') if site_id else 'Org'
                
                # Extract score from text or metric_value
                score_text = self._extract_score_display(insight)
                
                # Build classifier cells
                classifier_data = insight.get('classifier_data', {})
                classifier_cells = ""
                for c_name in expected_classifiers:
                    c_data = classifier_data.get(c_name)
                    if c_data:
                        pct = c_data['percent_degraded']
                        cell_parts = [f"{pct}% degraded"]
                        if c_data.get('num_users') is not None:
                            cell_parts.append(f"users={c_data['num_users']}")
                        if c_data.get('num_aps') is not None:
                            cell_parts.append(f"aps={c_data['num_aps']}")
                        cell_value = ", ".join(cell_parts)
                        # Color-code based on degradation percentage
                        if pct >= 20.0:
                            cell_style = 'color: #d32f2f; font-weight: bold;'
                        elif pct >= 10.0:
                            cell_style = 'color: #e65100;'
                        elif pct > 0:
                            cell_style = 'color: #f57c00;'
                        else:
                            cell_style = 'color: #388e3c;'
                        classifier_cells += f'<td class="classifier-value" style="{cell_style}">{html.escape(cell_value)}</td>'
                    else:
                        classifier_cells += '<td class="no-data">No data</td>'
                
                rows.append(
                    "<tr>"
                    f'<td style="color: {sev_color}; font-weight: bold;">{html.escape(priority_label)}</td>'
                    f"<td>{html.escape(str(site_name))}</td>"
                    f"<td>{html.escape(score_text)}</td>"
                    f"{classifier_cells}"
                    "</tr>"
                )
            
            if not rows:
                continue
            
            # Determine header color based on worst severity in group
            worst_sev = min(severity_rank.get(i.get('severity', 'info'), 3) for i in group_insights)
            header_bg = {0: '#d32f2f', 1: '#e65100', 2: '#f57c00', 3: '#388e3c'}.get(worst_sev, '#455a64')
            
            table = (
                f'<h4 style="margin: 15px 0 5px 0; color: {header_bg};">'
                f'{html.escape(display_name)}</h4>'
                f'<table class="insights-table" style="margin-bottom: 15px;">'
                f'<thead><tr style="background-color: {header_bg};">'
                f'{header_cols}'
                f'</tr></thead>'
                f'<tbody>'
                + "".join(rows)
                + '</tbody></table>'
            )
            tables_html.append(table)
        
        return "\n".join(tables_html)
    
    def _extract_score_display(self, insight: Dict) -> str:
        """Extract a clean score display string from an insight."""
        text = insight.get('text', '')
        # Try to extract score value like "75.4%" or "-56.1 dBm (88.6%)"
        if ':' in text:
            # Get the part after the first colon, before the dash
            score_part = text.split(':', 1)[1].strip()
            if ' - ' in score_part:
                score_part = score_part.split(' - ')[0].strip()
            return score_part
        # Fallback to metric_value
        mv = insight.get('metric_value')
        if mv is not None:
            return f"{mv * 100:.1f}%"
        return 'N/A'
    
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
        return str(report_path)
    
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
        
        dashboard_text = ""
        with open(dashboard_path, 'w') as f:
            dashboard_text += "=" * 70 + "\n"
            dashboard_text += "INFRASTRUCTURE HEALTH DASHBOARD\n"
            dashboard_text += "=" * 70 + "\n\n"
            
            dashboard_text += f"Generated: {timestamp}\n"
            dashboard_text += f"Overall Status: {status_symbols.get(health_status['overall_health'], health_status['overall_health'])}\n\n"
            
            # Priority-based action recommendations
            dashboard_text += "ACTION RECOMMENDATIONS (BY PRIORITY)\n"
            dashboard_text += "-" * 70 + "\n"
            
            if health_status['critical_insights'] > 0:
                dashboard_text += f"[CRIT] CRITICAL ({health_status['critical_insights']} issues)\n"
                dashboard_text += f"       {self._get_priority_action_text('critical')}\n"
                dashboard_text += "       - Investigate immediately\n"
                dashboard_text += "       - Engage incident response team\n"
                dashboard_text += "       - Estimate resolution time\n\n"
            
            if health_status['major_insights'] > 0:
                dashboard_text += f"[FAIL] MAJOR ({health_status['major_insights']} issues)\n"
                dashboard_text += f"       {self._get_priority_action_text('major')}\n"
                dashboard_text += "       - Create tickets for remediation\n"
                dashboard_text += "       - Schedule maintenance window\n"
                dashboard_text += "       - Document impact and workarounds\n\n"
            
            if health_status['warning_insights'] > 0:
                dashboard_text += f"[WARN] WARNING ({health_status['warning_insights']} issues)\n"
                dashboard_text += f"       {self._get_priority_action_text('warning')}\n"
                dashboard_text += "       - Monitor trending metrics\n"
                dashboard_text += "       - Plan preventive maintenance\n"
                dashboard_text += "       - Update runbooks if applicable\n\n"
            
            if health_status['info_insights'] > 0 and (health_status['critical_insights'] == 0 and 
                                                        health_status['major_insights'] == 0 and 
                                                        health_status['warning_insights'] == 0):
                dashboard_text += f"[INFO] All systems normal\n"
                dashboard_text += "       Continue routine monitoring\n\n"
            
            # Summary statistics
            dashboard_text += "HEALTH STATISTICS\n"
            dashboard_text += "-" * 70 + "\n"
            total_issues = (health_status['critical_insights'] + 
                          health_status['major_insights'] + 
                          health_status['warning_insights'])
            
            dashboard_text += f"Total Issues:    {total_issues}\n"
            dashboard_text += f"  [CRIT] Critical:   {health_status['critical_insights']}\n"
            dashboard_text += f"  [WARN] Major:      {health_status['major_insights']}\n"
            dashboard_text += f"  [!] Warning:       {health_status['warning_insights']}\n"
            dashboard_text += f"  [i] Info:          {health_status['info_insights']}\n\n"
            
            # Site status grid
            dashboard_text += "SITE STATUS GRID\n"
            dashboard_text += "-" * 70 + "\n"
            
            healthy_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'HEALTHY')
            degraded_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'DEGRADED')
            unhealthy_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'UNHEALTHY')
            critical_sites = sum(1 for s in health_status['sites_status'].values() if s['status'] == 'CRITICAL')
            
            dashboard_text += f"Healthy:    {healthy_sites}\n"
            dashboard_text += f"Degraded:   {degraded_sites}\n"
            dashboard_text += f"Unhealthy:  {unhealthy_sites}\n"
            dashboard_text += f"Critical:   {critical_sites}\n\n"
            
            # Individual site status - sorted by severity (critical sites first)
            dashboard_text += "INDIVIDUAL SITE STATUS (PRIORITY-ORDERED)\n"
            dashboard_text += "-" * 70 + "\n"
            dashboard_text += f"{'Site Name':<30} | {'Status':<12} | Insights\n"
            dashboard_text += "-" * 70 + "\n"
            
            # Sort sites by severity for display
            severity_order = {'CRITICAL': 0, 'UNHEALTHY': 1, 'DEGRADED': 2, 'HEALTHY': 3}
            sorted_sites = sorted(health_status['sites_status'].items(), 
                                key=lambda x: severity_order.get(x[1]['status'], 4))
            
            for site_name, site_info in sorted_sites:
                status = site_info['status']
                symbol = status_symbols.get(status, status)
                dashboard_text += f"{site_name:<30} | {symbol:<12} | {site_info['insight_count']}\n"
            
            dashboard_text += "\n" + "=" * 70 + "\n"
            dashboard_text += "Dashboard generated successfully\n"
            dashboard_text += "=" * 70 + "\n"
            
            f.write(dashboard_text)
        
        self.logger.info(f"Health Dashboard generated: {dashboard_name}")
        return dashboard_text
    
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
