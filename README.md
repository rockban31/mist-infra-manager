# Mist Infrastructure Manager

A proactive infrastructure management tool for Juniper Mist networks. Monitors network health, analyzes trends, and sends automated email alerts with detailed reports.

## ✅ Current Features

- **Infrastructure Monitoring**: Track SLE metrics across all sites
- **Insights Analysis**: Identify performance issues and anomalies
- **Summary Reports**: Comprehensive health reports with detailed metrics
- **Health Dashboard**: Visual status overview with action recommendations
- **Trend Analysis**: Day-over-day metric comparison with degradation detection
- **Email Notifications**: Automated alerts with dashboard details and attachments
- **Historical Data**: 7-day rolling retention with automatic cleanup
- **Daemon Mode**: Continuous monitoring with configurable intervals

## Prerequisites

- Python 3.9+
- Juniper Mist account with API token
- SMTP server access (for email notifications)

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Edit `config/config.yaml`:
```yaml
mist:
  api_token: "YOUR_API_TOKEN"

notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "exchrelay.global.tesco.org"
    smtp_port: 25
    from_address: "mist-infra-manager@company.com"
    recipients:
      - "ops@company.com"
```

### 3. Run

```bash
# Generate single report with email notification
.venv\Scripts\python.exe src/main.py --mode report --verbose

# Run in daemon mode (continuous monitoring)
.venv\Scripts\python.exe src/main.py --daemon --interval 15 --verbose

# View help
.venv\Scripts\python.exe src/main.py --help
```

## Command Options

| Option | Description |
|--------|-------------|
| `--mode {report\|monitor\|insights\|all}` | Monitoring mode (default: all) |
| `--daemon` | Run continuously in background |
| `--interval MINUTES` | Monitoring interval (default: 15) |
| `--config PATH` | Configuration file path |
| `--verbose` | Enable detailed logging |

## Output Files

Reports are saved to `reports/`:

- **SUMMARY_REPORT_*.txt** - Infrastructure summary
- **HEALTH_DASHBOARD_*.txt** - Status dashboard with recommendations
- **HEALTH_DASHBOARD_*.json** - Machine-readable dashboard
- **reports/history/** - 7-day rolling historical data

## Email Alerts

Automated alerts are sent for:
- **Critical**: 1+ critical infrastructure issues
- **Major**: 1+ major issues (without critical)
- **Trend**: Degradation in day-over-day metrics

Each email includes:
- Full infrastructure health dashboard
- Summary report as attachment
- Actionable recommendations by severity

## Configuration

### Getting Your API Token

1. Log in to https://manage.mist.com
2. Go to Organization > Settings > API Tokens
3. Create a new token
4. Add to `config/config.yaml`

### SMTP Configuration

**Tesco Relay (Current):**
```yaml
smtp_server: "exchrelay.global.tesco.org"
smtp_port: 25
use_tls: false
```

**Gmail:**
```yaml
smtp_server: "smtp.gmail.com"
smtp_port: 587
use_tls: true
smtp_user: "your-email@gmail.com"
smtp_password: "app-password"  # Use app password if 2FA enabled
```

**Office365:**
```yaml
smtp_server: "smtp.office365.com"
smtp_port: 587
use_tls: true
```

### History Configuration

```yaml
history:
  directory: "reports/history"  # Where to store reports
  keep_days: 7                  # 7-day retention
```

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
- Test procedures (10 test cases)
- Troubleshooting steps
- Windows PowerShell commands
- SMTP connectivity testing

## Project Structure

```
mist-infra-manager/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── mist_client.py     # API client
│   ├── report_generator.py
│   ├── insights_analyzer.py
│   ├── trend_analyzer.py
│   ├── sle_monitor.py
│   └── notification_service.py
├── config/
│   ├── config.yaml        # Configuration (create from template)
│   └── config.yaml.template
├── reports/               # Generated reports
│   └── history/          # Historical reports
├── QUICK_START.md        # Quick start guide
├── TESTING_GUIDE.md      # Test procedures
└── NEXT_STEPS.md         # Next phase planning
```

## Logging

- **Console**: Real-time formatted output
- **File**: `mist_infra_manager.log` - Detailed debug info

View logs:
```powershell
Get-Content mist_infra_manager.log -Tail 50
Get-Content mist_infra_manager.log -Wait  # Real-time
```

## Troubleshooting

### No API Token Error
Add valid token to `config/config.yaml` under `mist.api_token`

### SMTP Connection Failed
- Verify SMTP server and port
- Check firewall allows outbound SMTP
- Test connection manually (see TESTING_GUIDE.md)

### No Reports Generated
- Verify API token is valid
- Check network connectivity
- Ensure organization has sites configured

### Email Not Sending
1. Verify SMTP config in `config/config.yaml`
2. Test SMTP connectivity (see TESTING_GUIDE.md)
3. Check logs: `Get-Content mist_infra_manager.log | Select-String "Email"`

## Next Steps

See [NEXT_STEPS.md](NEXT_STEPS.md) for:
- Remaining tests to execute
- Production deployment checklist
- Performance considerations
- Future enhancements

## Resources

- **Mist API**: https://api.mist.com/api/v1/docs/
- **Support**: See QUICK_START.md and TESTING_GUIDE.md
- **Configuration**: See config/config.yaml.template

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** January 29, 2026
