#!/usr/bin/env python3
"""
Mist Infrastructure Manager - Main Application
Proactive infrastructure management using Juniper Mist API
"""

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

import schedule
import yaml

from mist_client import MistAPIClient
from sle_monitor import SLEMonitor
from insights_analyzer import InsightsAnalyzer
from report_generator import ReportGenerator
from trend_analyzer import TrendAnalyzer
from notification_service import NotificationService


# Global flag for graceful shutdown
_shutdown_requested = False


def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    # Custom formatter for cleaner console output
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - shorter format for readability
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # File handler - detailed format for debugging
    file_handler = logging.FileHandler('mist_infra_manager.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_requested = True


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_monitoring_cycle(client, config, mode: str, logger):
    """Execute a single monitoring cycle."""
    logger.info("="  * 60)
    logger.info("Starting monitoring cycle")
    
    try:
        if mode in ['monitor', 'all']:
            logger.info("Running SLE monitoring...")
            sle_monitor = SLEMonitor(client)
            sle_monitor.run_monitoring()
        
        if mode in ['insights', 'all']:
            logger.info("Analyzing insights...")
            insights_analyzer = InsightsAnalyzer(client)
            insights_analyzer.analyze_insights()
        
        if mode in ['report', 'all']:
            logger.info("Generating infrastructure report...")
            
            # Initialize trend analyzer
            history_config = config.get('history', {})
            trend_analyzer = TrendAnalyzer(
                history_dir=history_config.get('directory', 'reports/history'),
                keep_days=history_config.get('keep_days', 7)
            )
            
            # Generate report with trend analysis
            report_generator = ReportGenerator(client, trend_analyzer)
            report_result = report_generator.generate_report()
            
            # Send notifications if enabled
            notification_config = config.get('notifications', {})
            if notification_config.get('enabled', False):
                notification_service = NotificationService(notification_config)
                health_status = report_result.get('health_status', {})
                trends = report_result.get('trends', {})
                
                # Send critical alerts
                if health_status.get('critical_insights', 0) > 0:
                    logger.info("Sending critical alert notification...")
                    notification_service.send_critical_alert({
                        'critical_insights': health_status.get('critical_insights', 0),
                        'affected_sites': len([s for s in health_status.get('sites_status', {}).values() 
                                             if s.get('status') == 'CRITICAL'])
                    })
                
                # Send major alerts
                if health_status.get('major_insights', 0) > 0 and health_status.get('critical_insights', 0) == 0:
                    logger.info("Sending major alert notification...")
                    notification_service.send_major_alert({
                        'major_insights': health_status.get('major_insights', 0),
                        'affected_sites': len([s for s in health_status.get('sites_status', {}).values() 
                                             if s.get('status') == 'UNHEALTHY'])
                    })
                
                # Send trend degradation alerts
                if trends and trends.get('degradation_alerts'):
                    logger.info("Sending trend degradation alert notification...")
                    notification_service.send_trend_alert(trends)
        
        logger.info("Monitoring cycle completed")
        
    except Exception as e:
        logger.warning(f"Monitoring cycle encountered issues: {e}")
        logger.info("Continuing despite errors...")


def run_daemon(client, config, mode: str, interval_minutes: int, logger):
    """
    Run the monitoring tool in daemon mode with scheduled intervals.
    
    Args:
        client: MistAPIClient instance
        config: Configuration dictionary
        mode: Operation mode (monitor, insights, report, all)
        interval_minutes: Minutes between monitoring cycles
        logger: Logger instance
    """
    global _shutdown_requested
    
    logger.info(f"Starting daemon mode - monitoring every {interval_minutes} minute(s)")
    logger.info("Press Ctrl+C to stop")
    
    # Run immediately on startup
    run_monitoring_cycle(client, config, mode, logger)
    
    # Schedule subsequent runs
    schedule.every(interval_minutes).minutes.do(
        run_monitoring_cycle, client, config, mode, logger
    )
    
    # Main loop
    while not _shutdown_requested:
        schedule.run_pending()
        time.sleep(1)
    
    logger.info("Daemon shutdown complete")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='Proactive Mist Infrastructure Management Tool'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--mode',
        type=str,
        choices=['monitor', 'insights', 'report', 'all'],
        default='all',
        help='Operation mode'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run continuously with scheduled monitoring intervals'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=None,
        help='Monitoring interval in minutes (overrides config file)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Mist Infrastructure Manager")
    
    try:
        # Initialize Mist API client
        client = MistAPIClient(config_path=args.config)
        
        # Load configuration
        config = load_config(args.config)
        
        if args.daemon:
            # Load interval from config or use argument/default
            interval = args.interval
            if interval is None:
                interval = config.get('monitoring', {}).get('interval_minutes', 15)
            
            run_daemon(client, config, args.mode, interval, logger)
        else:
            # Single run mode (original behavior)
            run_monitoring_cycle(client, config, args.mode, logger)
            logger.info("Mist Infrastructure Manager completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
