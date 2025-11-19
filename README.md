# Mist Infrastructure Manager

A proactive infrastructure management tool for Juniper Mist networks using API integration. This tool monitors Service Level Expectations (SLE), analyzes insights, and provides actionable recommendations for network infrastructure health.

## Features

- **SLE Monitoring**: Track and monitor Service Level Expectations across all sites
- **Insights Analysis**: Analyze Mist insights and identify patterns requiring attention
- **Proactive Alerting**: Automatic detection of threshold violations and anomalies
- **Multi-Site Support**: Manage multiple sites from a single interface
- **Detailed Reporting**: Comprehensive reports on network health and performance

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

Run all monitoring and analysis:
```bash
python src/main.py
```

### Specific Operations

Monitor SLE metrics only:
```bash
python src/main.py --mode monitor
```

Analyze insights only:
```bash
python src/main.py --mode insights
```

Generate reports:
```bash
python src/main.py --mode report
```

### Advanced Options

Enable verbose logging:
```bash
python src/main.py --verbose
```

Use a custom configuration file:
```bash
python src/main.py --config /path/to/config.yaml
```

## Project Structure

```
mist-infra-manager/
├── src/
│   ├── main.py              # Main application entry point
│   ├── mist_client.py       # Mist API client
│   ├── sle_monitor.py       # SLE monitoring module
│   └── insights_analyzer.py # Insights analysis module
├── config/
│   ├── config.yaml.template # Configuration template
│   └── config.yaml          # Your configuration (gitignored)
├── docs/                    # Additional documentation
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## SLE Metrics Monitored

- **Successful Connect**: Client connection success rate
- **Time to Connect**: Average time for clients to connect
- **Throughput**: Network throughput performance
- **Capacity**: AP capacity utilization
- **Roaming**: Client roaming success rate

## Insights Analysis

The tool analyzes Mist insights and categorizes them by:
- **Severity**: Critical, Major, Minor, Warning, Info
- **Type**: Various insight types from Mist platform
- **Site**: Per-site analysis and reporting

### Proactive Recommendations

Based on the analysis, the tool provides:
- Urgent action items for critical issues
- Pattern detection across multiple occurrences
- Site-specific issue prioritization
- Root cause investigation suggestions

## Output

The application generates:
- Console output with real-time monitoring status
- Log file (`mist_infra_manager.log`) with detailed information
- Summary reports with actionable recommendations

## Scheduling (Optional)

To run the tool on a schedule, you can use:

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
