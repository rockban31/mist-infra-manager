# Mist Infrastructure Manager

A proactive infrastructure management tool for Juniper Mist networks. Monitors network health, analyzes trends, and sends automated email alerts with detailed reports.

## 🎯 Project Status

✅ **Phase 1 Complete** - Production Ready  
✅ **All Tests Passed** - 6/6 (100%)  
✅ **API Integration** - 35 SLE metrics accessible  
✅ **Enhanced Monitoring** - 21 total insights tracked

## ✅ Current Features

### Core Monitoring
- **Infrastructure Monitoring**: Track 35 SLE metrics across all sites
- **Insights Analysis**: 21 comprehensive insights (15 standard + 6 enhanced)
  - Capacity, Roaming, Successful Connect, Time-to-Connect, AP Health
  - **NEW:** Throughput metrics (3 sites)
  - **NEW:** Coverage metrics (3 sites)
- **Summary Reports**: Comprehensive health reports with detailed metrics
- **Health Dashboard**: Visual status overview with action recommendations

### Automation & Analysis
- **Trend Analysis**: Day-over-day metric comparison with degradation detection
- **Email Notifications**: Automated alerts with dashboard details and attachments
  - Critical alerts for urgent issues
  - Major alerts for high-priority issues
  - Trend alerts for performance degradation
- **Historical Data**: 7-day rolling retention with automatic cleanup
- **Daemon Mode**: Continuous monitoring with configurable intervals

## Prerequisites

- Python 3.9+ (tested with Python 3.13)
- Juniper Mist account with API token
- SMTP server access (for email notifications)
- Network access to api.eu.mist.com (or your regional API endpoint)

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

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

# Run in daemon mode (continuous monitoring every 15 minutes)
.venv\Scripts\python.exe src/main.py --daemon --interval 15 --verbose

# View help
.venv\Scripts\python.exe src/main.py --help
```

## Monitored Metrics (21 Total)

### Standard Insights (15 metrics from Insights API)
- **Capacity** - Network capacity utilization per site
- **Roaming** - Client roaming success rate
- **Successful Connect** - Connection success percentage
- **Time-to-Connect** - Average connection time
- **AP Health** - Access point health status

### Enhanced SLE Metrics (6 additional)
- **Throughput** - Network throughput performance (3 sites)
- **Coverage** - WiFi coverage quality (3 sites)

**Note:** System queries 35 available SLE metrics but reports on 21 key performance indicators.

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

- **SUMMARY_REPORT_*.txt** - Infrastructure summary with all 21 insights
- **HEALTH_DASHBOARD_*.txt** - Status dashboard with recommendations
- **HEALTH_DASHBOARD_*.json** - Machine-readable dashboard (0.67KB per report)
- **reports/history/YYYY-MM-DD/** - 7-day rolling historical data

### Insight Breakdown Example
- **Critical:** 0-3 (urgent infrastructure issues)
- **Major:** 2-3 (high-priority capacity issues)
- **Warning:** 4-6 (monitor closely - roaming, connectivity)
- **Info:** 9-12 (healthy metrics including throughput)

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

✅ **All Tests Passed (6/6)** - February 5, 2026

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
- Test procedures and results
- Troubleshooting steps
- Windows PowerShell commands
- SMTP connectivity testing

### Test Results Summary
| Test | Status | Result |
|------|--------|--------|
| Basic Report Generation | ✅ PASS | 21 insights captured |
| Insights Count | ✅ PASS | Target achieved (15→21) |
| Throughput/Coverage | ✅ PASS | 6 metrics added |
| History Retention | ✅ PASS | 7-day retention working |
| API Endpoints | ✅ PASS | 35 metrics accessible |
| Email Notifications | ✅ PASS | Alerts sent successfully |

## Project Structure

```
mist-infra-manager/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── mist_client.py     # API client (fixed SLE endpoints)
│   ├── report_generator.py # Enhanced with throughput/coverage
│   ├── insights_analyzer.py
│   ├── trend_analyzer.py
│   ├── sle_monitor.py
│   └── notification_service.py
├── config/
│   ├── config.yaml        # Configuration (create from template)
│   └── config.yaml.template
├── reports/               # Generated reports
│   └── history/          # 7-day historical data (by date)
├── bruno/                # API testing collection (Bruno/Postman)
│   ├── *.bru            # 10 API endpoint tests
│   └── README.md        # API documentation
├── README.md            # This file
├── QUICK_START.md       # Quick start guide
├── TESTING_GUIDE.md     # Test procedures and results
├── EXECUTIVE_SUMMARY.md # Project summary for leadership
├── PHASE_1_COMPLETE.md  # Phase 1 completion report
├── NEXT_STEPS.md        # Deployment and Phase 2 roadmap
└── requirements.txt     # Python dependencies
```

## Key Files

### Documentation
- **README.md** - Main documentation (this file)
- **EXECUTIVE_SUMMARY.md** - Leadership brief
- **QUICK_START.md** - 5-minute setup guide
- **TESTING_GUIDE.md** - Test procedures and results
- **PHASE_1_COMPLETE.md** - Phase 1 completion details

### Configuration
- **config/config.yaml** - Active configuration (not in git)
- **config/config.yaml.template** - Configuration template

### Source Code
- **src/main.py** - Application entry point
- **src/mist_client.py** - Mist API integration
- **src/report_generator.py** - Report generation with enhanced metrics
- **src/notification_service.py** - Email alerts

### API Testing
- **bruno/** - Bruno API collection (10 endpoints tested)

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
- Production deployment checklist
- Windows Task Scheduler setup
- Performance considerations
- Phase 2 enhancement roadmap

### Immediate Actions
1. ✅ Phase 1 complete - all tests passed
2. **Deploy to production** - system ready for live monitoring
3. **Schedule automated runs** - 15-minute intervals recommended
4. **Monitor first 5 cycles** - verify email delivery

### Future Enhancements (Phase 2)
- Health scoring system (0-100 per site)
- Predictive alerts (ML-based trend prediction)
- Enhanced analytics dashboard
- Custom alerting rules per site

## Recent Updates

### February 5, 2026 - v1.1.0
- ✅ **Enhanced Metrics:** Added throughput and coverage monitoring (21 total insights)
- ✅ **API Fix:** Corrected SLE endpoint URLs for full metric access
- ✅ **Testing Complete:** All 6 tests passed successfully
- ✅ **Production Ready:** System verified and deployed

### January 29, 2026 - v1.0.0
- ✅ Initial release with 15 standard insights
- ✅ Trend analysis and email notifications
- ✅ 7-day historical data retention

## Resources

- **Mist API Documentation**: https://api.mist.com/api/v1/docs/
- **API Regional Endpoints**: 
  - EU: https://api.eu.mist.com/api/v1
  - Global: https://api.mist.com/api/v1
- **Project Documentation**: See EXECUTIVE_SUMMARY.md, QUICK_START.md
- **API Testing**: See bruno/ directory for Bruno/Postman collection

---

**Status:** ✅ Production Ready | Phase 1 Complete  
**Version:** 1.1.0  
**Last Updated:** February 5, 2026  
**Test Status:** 6/6 Passed (100%)  
**Monitored Sites:** 3 (Phoenix, Sonic, StarGate)  
**Total Insights:** 21 (15 standard + 6 enhanced)
