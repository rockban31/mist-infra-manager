#!/usr/bin/env python3
"""
Mist Infrastructure Manager - Main Application
Proactive infrastructure management using Juniper Mist API
"""

import argparse
import logging
from pathlib import Path

from mist_client import MistAPIClient
from sle_monitor import SLEMonitor
from insights_analyzer import InsightsAnalyzer


def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mist_infra_manager.log'),
            logging.StreamHandler()
        ]
    )


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
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Mist Infrastructure Manager")
    
    try:
        # Initialize Mist API client
        client = MistAPIClient(config_path=args.config)
        
        if args.mode in ['monitor', 'all']:
            logger.info("Starting SLE monitoring...")
            sle_monitor = SLEMonitor(client)
            sle_monitor.run_monitoring()
        
        if args.mode in ['insights', 'all']:
            logger.info("Analyzing insights...")
            insights_analyzer = InsightsAnalyzer(client)
            insights_analyzer.analyze_insights()
        
        if args.mode in ['report', 'all']:
            logger.info("Generating infrastructure report...")
            # Future: Add reporting functionality
            
        logger.info("Mist Infrastructure Manager completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
