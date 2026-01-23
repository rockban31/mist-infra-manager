"""
Notification Service
Sends email alerts for critical infrastructure issues
"""

import logging
import smtplib
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class NotificationService:
    """Handle email notifications for alerts."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize Notification Service.
        
        Args:
            config: Email configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.enabled = self.config.get('enabled', False)
        self.email_config = self.config.get('email', {})
    
    def is_enabled(self) -> bool:
        """Check if notification service is enabled."""
        return self.enabled and self.email_config.get('enabled', False)
    
    def send_critical_alert(self, alert_data: Dict) -> bool:
        """
        Send alert for critical issues.
        
        Args:
            alert_data: Alert information
            
        Returns:
            True if sent successfully
        """
        if not self.is_enabled():
            self.logger.debug("Notifications disabled, skipping critical alert")
            return False
        
        try:
            subject = "🚨 CRITICAL: Mist Infrastructure Alert"
            body = self._format_critical_alert(alert_data)
            
            return self.send_email(subject, body)
        
        except Exception as e:
            self.logger.error(f"Error sending critical alert: {e}")
            return False
    
    def send_major_alert(self, alert_data: Dict) -> bool:
        """
        Send alert for major issues.
        
        Args:
            alert_data: Alert information
            
        Returns:
            True if sent successfully
        """
        if not self.is_enabled():
            self.logger.debug("Notifications disabled, skipping major alert")
            return False
        
        try:
            subject = "⚠️  MAJOR: Mist Infrastructure Alert"
            body = self._format_major_alert(alert_data)
            
            return self.send_email(subject, body)
        
        except Exception as e:
            self.logger.error(f"Error sending major alert: {e}")
            return False
    
    def send_trend_alert(self, trend_data: Dict) -> bool:
        """
        Send alert for degradation trends.
        
        Args:
            trend_data: Trend analysis data
            
        Returns:
            True if sent successfully
        """
        if not self.is_enabled():
            self.logger.debug("Notifications disabled, skipping trend alert")
            return False
        
        if not trend_data.get('degradation_alerts'):
            return False
        
        try:
            subject = "📈 TREND: Infrastructure Degradation Detected"
            body = self._format_trend_alert(trend_data)
            
            return self.send_email(subject, body)
        
        except Exception as e:
            self.logger.error(f"Error sending trend alert: {e}")
            return False
    
    def send_email(self, subject: str, body: str) -> bool:
        """
        Send email notification.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully
        """
        try:
            if not self.email_config.get('recipients'):
                self.logger.warning("No email recipients configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from_address', 'noreply@mist-infra-manager.local')
            msg['To'] = ", ".join(self.email_config['recipients'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_user = self.email_config.get('smtp_user')
            smtp_password = self.email_config.get('smtp_password')
            use_tls = self.email_config.get('use_tls', True)
            
            self.logger.debug(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                if use_tls:
                    server.starttls()
                
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {len(self.email_config['recipients'])} recipient(s)")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            return False
        
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _format_critical_alert(self, alert_data: Dict) -> str:
        """Format critical alert HTML body."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #d32f2f; color: white; padding: 20px; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .alert-box {{ background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 10px 0; }}
                .metric {{ background-color: white; padding: 10px; margin: 5px 0; }}
                .footer {{ font-size: 12px; color: #666; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 CRITICAL INFRASTRUCTURE ALERT</h1>
            </div>
            <div class="content">
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="alert-box">
                    <h2>Critical Issues Detected</h2>
                    <p><strong>Critical Insights:</strong> {alert_data.get('critical_insights', 0)}</p>
                    <p><strong>Overall Health:</strong> CRITICAL</p>
                </div>
                
                <h3>Impact Summary</h3>
                <div class="metric">
                    <p><strong>Affected Sites:</strong> {alert_data.get('affected_sites', 0)}</p>
                </div>
                
                <h3>Immediate Actions Required</h3>
                <ul>
                    <li>Check dashboard for affected infrastructure</li>
                    <li>Review detailed logs and insights</li>
                    <li>Activate incident response procedures</li>
                    <li>Notify operations team</li>
                </ul>
                
                <h3>Dashboard Link</h3>
                <p><a href="http://localhost:8080/dashboard">View Infrastructure Dashboard</a></p>
                
            </div>
            <div class="footer">
                <p>Mist Infrastructure Manager | Automated Alert</p>
                <p>Please do not reply to this email</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _format_major_alert(self, alert_data: Dict) -> str:
        """Format major alert HTML body."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #f57c00; color: white; padding: 20px; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .alert-box {{ background-color: #ffe0b2; border-left: 4px solid #f57c00; padding: 15px; margin: 10px 0; }}
                .metric {{ background-color: white; padding: 10px; margin: 5px 0; }}
                .footer {{ font-size: 12px; color: #666; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️  MAJOR INFRASTRUCTURE ALERT</h1>
            </div>
            <div class="content">
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="alert-box">
                    <h2>Major Issues Detected</h2>
                    <p><strong>Major Insights:</strong> {alert_data.get('major_insights', 0)}</p>
                    <p><strong>Overall Health:</strong> DEGRADED</p>
                </div>
                
                <h3>Issue Summary</h3>
                <div class="metric">
                    <p><strong>Affected Sites:</strong> {alert_data.get('affected_sites', 0)}</p>
                </div>
                
                <h3>Recommended Actions</h3>
                <ul>
                    <li>Monitor the situation closely</li>
                    <li>Review affected infrastructure in dashboard</li>
                    <li>Prepare contingency plans</li>
                    <li>Keep team on standby</li>
                </ul>
                
                <h3>Dashboard Link</h3>
                <p><a href="http://localhost:8080/dashboard">View Infrastructure Dashboard</a></p>
                
            </div>
            <div class="footer">
                <p>Mist Infrastructure Manager | Automated Alert</p>
                <p>Please do not reply to this email</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _format_trend_alert(self, trend_data: Dict) -> str:
        """Format trend alert HTML body."""
        degradation_items = ""
        for alert in trend_data.get('degradation_alerts', []):
            degradation_items += f"""
                <div style="background-color: white; padding: 10px; margin: 5px 0;">
                    <p><strong>{alert['metric']}</strong></p>
                    <p>Previous: {alert['previous']:.1f} → Current: {alert['current']:.1f}</p>
                    <p>Change: {alert['change_percent']:+.1f}% {alert['indicator']}</p>
                </div>
            """
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #1976d2; color: white; padding: 20px; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .alert-box {{ background-color: #e3f2fd; border-left: 4px solid #1976d2; padding: 15px; margin: 10px 0; }}
                .footer {{ font-size: 12px; color: #666; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 INFRASTRUCTURE TREND ALERT</h1>
            </div>
            <div class="content">
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="alert-box">
                    <h2>Degradation Detected</h2>
                    <p>Infrastructure metrics are trending negatively compared to previous day.</p>
                </div>
                
                <h3>Affected Metrics</h3>
                {degradation_items}
                
                <h3>Next Steps</h3>
                <ul>
                    <li>Monitor trends closely over the next 24 hours</li>
                    <li>Review recent changes to infrastructure</li>
                    <li>Check for external factors affecting performance</li>
                    <li>Consider proactive scaling if trend continues</li>
                </ul>
                
                <h3>Dashboard Link</h3>
                <p><a href="http://localhost:8080/dashboard">View Infrastructure Dashboard</a></p>
                
            </div>
            <div class="footer">
                <p>Mist Infrastructure Manager | Automated Alert</p>
                <p>Please do not reply to this email</p>
            </div>
        </body>
        </html>
        """
        return html
