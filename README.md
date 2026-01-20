# Mist Infrastructure Manager

A proactive infrastructure management tool for Juniper Mist networks using API integration. This tool monitors Service Level Expectations (SLE), analyzes SLE metrics as insights, and generates comprehensive reports with actionable recommendations for network infrastructure health.

## Features

- **SLE Monitoring**: Track and monitor Service Level Expectations across all sites
- **Insights Analysis**: Analyze SLE metrics and identify performance issues requiring attention
- **Summary Reports**: Comprehensive infrastructure health reports with detailed metrics
- **Health Dashboard**: Quick visual status of infrastructure health by site
- **Trend Analysis**: 24-hour trend analysis with recommendations and next steps
- **Proactive Alerting**: Automatic detection of threshold violations and anomalies
- **Multi-Site Support**: Manage multiple sites from a single interface
- **Severity Levels**: Critical, Major, Warning, and Info categorization for action prioritization

## Prerequisites

- Python 3.7 or higher
- Juniper Mist account with API access
- Valid Mist API token

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd mist-infra-manager
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API credentials:
```bash
# Copy the template configuration file
cp config/config.yaml.template config/config.yaml

# Edit config/config.yaml and add your Mist API token
```

## Configuration

### Getting Your API Token

1. Log in to your Mist dashboard at https://manage.mist.com
2. Navigate to Organization > Settings > API Tokens
3. Create a new API token with appropriate permissions
4. Copy the token to your `config/config.yaml` file

### Configuration File

Edit `config/config.yaml`:

```yaml
mist:
  api_token: "your_actual_api_token_here"
```

You can also customize SLE thresholds and monitoring intervals. See `config/config.yaml.template` for all available options.

## Usage

### Basic Usage

Run complete monitoring, analysis, and report generation:
```bash
python src/main.py
```

### Specific Operations

Monitor SLE metrics only:
```bash
python src/main.py --mode monitor
```

Analyze SLE metrics as insights:
```bash
python src/main.py --mode insights
```

Generate Summary Report, Health Dashboard, and Trend Analysis:
```bash
python src/main.py --mode report
```

Run all operations (equivalent to `python src/main.py`):
```bash
python src/main.py --mode all
```

### Daemon Mode (Continuous Monitoring)

Run continuously with built-in scheduling:
```bash
# Use interval from config file (default: 15 minutes)
python src/main.py --daemon

# Override interval via command line (e.g., every 5 minutes)
python src/main.py --daemon --interval 5

# Combine with other options
python src/main.py --daemon --mode report --verbose
```

The daemon runs immediately on startup, then repeats at the configured interval. Press `Ctrl+C` to stop gracefully.

### Advanced Options

Enable verbose debug logging:
```bash
python src/main.py --verbose
```

Use a custom configuration file:
```bash
python src/main.py --config /path/to/config.yaml
```

### View Reports

After running `python src/main.py --mode report`, reports are saved to the `reports/` directory:

```bash
# View latest summary report
cd reports
Get-Content (Get-ChildItem -File -Filter "SUMMARY*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# View latest health dashboard (text)
Get-Content (Get-ChildItem -File -Filter "HEALTH*txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# View latest health dashboard (JSON)
Get-Content (Get-ChildItem -File -Filter "HEALTH*json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

## Report Formats

The tool supports the following report formats for different use cases:

- **Text (`.txt`)**: Human-readable reports for monitoring and review
- **JSON (`.json`)**: Machine-readable format for API integration and automation

### Report Output Types

#### Summary Report
- Overall infrastructure health status
- Insight breakdown by severity level
- Per-site status with issue count
- Detailed list of all insights with metrics
- **Files**: `SUMMARY_REPORT_*.txt`

#### Health Dashboard (Text & JSON)
Quick status snapshot available in 2 formats:

**Text Format** (`*.txt`)
- ASCII-based layout for terminal viewing
- Site status grid showing current health
- Summary statistics

**JSON Format** (`*.json`)
- Programmatic access for automation
- Complete health data with timestamps
- Integration-ready structure

## Dashboard Improvements & Features

### Quick Wins (✅ Implemented)

These easy-to-implement features are now available:

1. **Multiple Export Formats**
   - JSON export for programmatic access
   - Text export for terminal viewing
   
2. **Health Status Indicators**
   - [CRIT] = Critical (< 70%)
   - [FAIL] = Unhealthy major issues (70-80%)
   - [WARN] = Warning state (80-90%)
   - [OK] = Healthy (≥ 90%)
   
3. **Site Status Grid**
   - All sites displayed in one table
   - Status and issue count at a glance
   - Sites ordered by severity (critical first)

4. **Alert Priority System** ✅ (NEW)
   - Insights sorted by severity: Critical → Major → Warning → Info
   - Critical alerts displayed first with action required notice
   - Priority-based action recommendations for each severity level
   - Site status ordered by severity for quick identification of problem areas
   - Each alert includes specific next steps based on priority

5. **Action Recommendations** ✅ (NEW)
   - **Critical**: Immediate investigation, incident response engagement
   - **Major**: Ticket creation, maintenance scheduling
   - **Warning**: Trend monitoring, preventive maintenance planning
   - **Info**: Routine monitoring status

### Medium Effort Enhancements (Planned)

These features will enhance the dashboard experience:

1. **Comparison with Previous Run**
   - Track metric trends over time
   - Alert on degradation patterns
   - Show improvement/decline status

2. **ASCII Art Visualization**
   - Performance bars (████ vs ░░░░)
   - Status indicators with consistent styling
   - Improved visual hierarchy

3. **Detailed Recommendations**
   - Actionable next steps per severity
   - Priority-based remediation guidance
   - Links to relevant documentation

4. **Email Report Generation**
   - Automated email delivery of reports
   - Formatted HTML for email clients
   - Attachment support for multiple formats

### Advanced Features (Future Roadmap)

Planned for future releases:

1. **Real-Time Watch Mode**
   - Live terminal dashboard updates
   - Continuous monitoring display
   - Auto-refresh with configurable intervals

2. **Compact CLI Dashboard**
   - Single-screen health overview
   - Color-coded status display
   - Minimal terminal footprint for continuous display

3. **Web Dashboard Interface**
   - Browser-based visualization
   - Interactive charts and tables
   - Historical data viewing and filtering

4. **Integration Capabilities**
   - Slack/Teams notifications for alerts
   - PagerDuty integration for incident management
   - Webhook support for custom integrations

5. **Multi-Organization Support**
   - Manage multiple organizations
   - Cross-org reporting
   - Consolidated health views



## Project Structure

```
mist-infra-manager/
├── src/
│   ├── main.py              # Main application entry point
│   ├── mist_client.py       # Mist API client
│   ├── sle_monitor.py       # SLE monitoring module
│   ├── insights_analyzer.py # Insights analysis module
│   └── report_generator.py  # Report generation module
├── config/
│   ├── config.yaml.template # Configuration template
│   └── config.yaml          # Your configuration (gitignored)
├── reports/                 # Generated reports (auto-created)
│   ├── SUMMARY_REPORT_*.txt        # Summary reports with detailed insights
│   ├── HEALTH_DASHBOARD_*.txt      # Health dashboard snapshots (text)
│   └── HEALTH_DASHBOARD_*.json     # Health dashboard snapshots (JSON)
├── bruno/                   # Bruno API collection files
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## SLE Metrics Monitored

The tool monitors the following Service Level Expectations (SLE) metrics for each site:

- **Successful Connect**: Client connection success rate (0-1, where 1 = 100%)
- **Time to Connect**: Average time for clients to connect to network
- **Throughput**: Network throughput performance metrics
- **Capacity**: AP capacity utilization (0-1)
- **Roaming**: Client roaming success rate (0-1)
- **AP Health**: Access Point health and availability

## Insights and Severity Levels

SLE metrics are converted to actionable insights with severity levels:

| Severity | Threshold | Action Required |
|----------|-----------|-----------------|
| **Critical** | < 0.70 (70%) | Immediate action required |
| **Major** | 0.70 - 0.80 (70-80%) | Address within 24 hours |
| **Warning** | 0.80 - 0.90 (80-90%) | Monitor and escalate if worsens |
| **Info** | ≥ 0.90 (90%) | Normal operation |

## Scheduling

### Built-in Daemon Mode (Recommended)

The simplest approach is to use the built-in daemon mode:
```bash
python src/main.py --daemon --interval 15
```

This keeps the tool running continuously with the specified interval.

### External Scheduling (Alternative)

If you prefer external scheduling:

**Windows Task Scheduler**:
1. Create a new task
2. Set trigger (e.g., every 15 minutes)

3. Action: `python D:\mist-infra-manager\src\main.py`

**Linux/Mac (cron)**:
```bash
# Edit crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/mist-infra-manager && python src/main.py
```

## Console Output Format

The application uses a clean, aligned console output format:
```
HH:MM:SS | LEVEL    | Message
13:45:06 | INFO     | Starting Mist Infrastructure Manager
13:45:07 | INFO     | Configuration loaded from config/config.yaml
13:45:08 | INFO     | Retrieved 3 sites
13:45:09 | WARNING  | Site Sonic: Capacity metric critical (69.6%)
```

Detailed logs are saved to `mist_infra_manager.log` for debugging and audit purposes.

## Security Best Practices

- **Never commit** your `config/config.yaml` file with actual API tokens
- Use environment variables for sensitive data in production
- Restrict API token permissions to minimum required
- Rotate API tokens regularly
- Review logs for any unauthorized access attempts

## Troubleshooting

### Authentication Errors
- Verify your API token is correct and active
- Check that the token has appropriate permissions
- Ensure your organization ID is accessible

### Connection Issues
- Verify network connectivity to api.mist.com
- Check firewall rules and proxy settings
- Review SSL/TLS certificate validation

### No Data Returned
- Verify sites exist in your organization
- Check that devices are online and reporting
- Review API token scope and permissions

## API Rate Limits

Be aware of Mist API rate limits:
- Default: 5000 requests per hour per organization
- Monitor your usage to avoid throttling
- Consider implementing caching for frequently accessed data

## Future Enhancements

- [ ] Email/SMS alerting for critical issues
- [ ] Dashboard web interface
- [ ] Historical trend analysis
- [ ] Integration with ticketing systems
- [ ] Custom report templates
- [ ] Multi-organization support

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is provided as-is for infrastructure management purposes.

## Support

For issues related to:
- **Mist API**: Contact Juniper Mist support
- **This Tool**: Open an issue in the repository

## Resources

- [Juniper Mist API Documentation](https://api.mist.com/api/v1/docs/)
- [Mist Support Portal](https://support.mist.com/)
- [Mist Community Forums](https://community.juniper.net/communities/community-home?CommunityKey=mist)
