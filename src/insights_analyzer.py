"""
Insights Analyzer
Analyzes Mist insights and provides proactive recommendations
"""

import logging
from typing import Dict, List
from collections import defaultdict


class InsightsAnalyzer:
    """Analyze Mist insights and generate actionable recommendations."""
    
    # Insight severity levels
    SEVERITY_LEVELS = {
        'critical': 4,
        'major': 3,
        'minor': 2,
        'warning': 1,
        'info': 0
    }
    
    def __init__(self, mist_client):
        """
        Initialize Insights Analyzer.
        
        Args:
            mist_client: MistAPIClient instance
        """
        self.client = mist_client
        self.logger = logging.getLogger(__name__)
    
    def analyze_insights(self):
        """Analyze insights across the organization."""
        self.logger.info("Starting insights analysis")
        
        try:
            insights = self.client.get_insights()
            
            if not insights:
                self.logger.info("No insights found")
                return
            
            # Categorize insights
            categorized = self._categorize_insights(insights)
            
            # Generate report
            self._generate_insights_report(categorized)
            
            # Identify proactive actions
            self._identify_proactive_actions(categorized)
        
        except Exception as e:
            self.logger.warning(f"Insights analysis unavailable: {str(e)[:100]}")
            self.logger.info("Skipping insights analysis - endpoint may not be available for your organization")
    
    def _categorize_insights(self, insights: List[Dict]) -> Dict:
        """
        Categorize insights by type and severity.
        
        Args:
            insights: List of insight dictionaries
            
        Returns:
            Dictionary with categorized insights
        """
        categorized = {
            'by_severity': defaultdict(list),
            'by_type': defaultdict(list),
            'by_site': defaultdict(list)
        }
        
        for insight in insights:
            severity = insight.get('severity', 'info').lower()
            insight_type = insight.get('type', 'unknown')
            site_id = insight.get('site_id', 'unknown')
            
            categorized['by_severity'][severity].append(insight)
            categorized['by_type'][insight_type].append(insight)
            categorized['by_site'][site_id].append(insight)
        
        return categorized
    
    def _generate_insights_report(self, categorized: Dict):
        """Generate and log insights report."""
        self.logger.info("=" * 60)
        self.logger.info("INSIGHTS ANALYSIS REPORT")
        self.logger.info("=" * 60)
        
        # Summary by severity
        self.logger.info("\nInsights by Severity:")
        for severity in ['critical', 'major', 'minor', 'warning', 'info']:
            count = len(categorized['by_severity'].get(severity, []))
            if count > 0:
                self.logger.info(f"  {severity.upper()}: {count}")
        
        # Summary by type
        self.logger.info("\nInsights by Type:")
        for insight_type, insights in categorized['by_type'].items():
            self.logger.info(f"  {insight_type}: {len(insights)}")
        
        # Critical and major insights details
        critical_insights = categorized['by_severity'].get('critical', [])
        major_insights = categorized['by_severity'].get('major', [])
        
        if critical_insights:
            self.logger.warning("\nCRITICAL INSIGHTS:")
            for insight in critical_insights:
                self._log_insight_details(insight)
        
        if major_insights:
            self.logger.warning("\nMAJOR INSIGHTS:")
            for insight in major_insights:
                self._log_insight_details(insight)
        
        self.logger.info("=" * 60)
    
    def _log_insight_details(self, insight: Dict):
        """Log details of a single insight."""
        insight_type = insight.get('type', 'Unknown')
        description = insight.get('description', 'No description')
        site_id = insight.get('site_id', 'Unknown')
        
        self.logger.warning(f"  Type: {insight_type}")
        self.logger.warning(f"  Site: {site_id}")
        self.logger.warning(f"  Description: {description}")
        
        # Log any additional relevant fields
        if 'device_name' in insight:
            self.logger.warning(f"  Device: {insight['device_name']}")
        if 'timestamp' in insight:
            self.logger.warning(f"  Time: {insight['timestamp']}")
        
        self.logger.warning("")
    
    def _identify_proactive_actions(self, categorized: Dict):
        """Identify and recommend proactive actions based on insights."""
        self.logger.info("PROACTIVE RECOMMENDATIONS:")
        
        actions = []
        
        # Check for patterns that require action
        critical_count = len(categorized['by_severity'].get('critical', []))
        major_count = len(categorized['by_severity'].get('major', []))
        
        if critical_count > 0:
            actions.append(
                f"URGENT: Address {critical_count} critical insight(s) immediately"
            )
        
        if major_count > 3:
            actions.append(
                f"Review and address {major_count} major insights to prevent degradation"
            )
        
        # Check for specific insight types
        for insight_type, insights in categorized['by_type'].items():
            if len(insights) > 2:
                actions.append(
                    f"Pattern detected: Multiple '{insight_type}' insights "
                    f"({len(insights)} occurrences) - investigate root cause"
                )
        
        # Check for site-specific issues
        for site_id, insights in categorized['by_site'].items():
            high_severity = [
                i for i in insights 
                if i.get('severity', 'info').lower() in ['critical', 'major']
            ]
            if len(high_severity) > 2:
                actions.append(
                    f"Site {site_id} has {len(high_severity)} high-severity insights "
                    f"- prioritize investigation"
                )
        
        # Log recommendations
        if actions:
            for idx, action in enumerate(actions, 1):
                self.logger.info(f"  {idx}. {action}")
        else:
            self.logger.info("  No immediate actions required")
        
        self.logger.info("")
    
    def get_insights_summary(self) -> Dict:
        """
        Get summary of current insights.
        
        Returns:
            Dictionary with insights summary
        """
        try:
            insights = self.client.get_insights()
            categorized = self._categorize_insights(insights)
            
            summary = {
                'total_insights': len(insights),
                'by_severity': {
                    severity: len(items)
                    for severity, items in categorized['by_severity'].items()
                },
                'by_type': {
                    insight_type: len(items)
                    for insight_type, items in categorized['by_type'].items()
                },
                'sites_affected': len(categorized['by_site'])
            }
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Error generating insights summary: {e}")
            return {}
