# Option A Implementation: Trend Analysis + Email Notifications

## Overview

This implementation adds proactive capabilities to the Mist Infrastructure Manager with the following features:

1. **Trend Analysis & Degradation Detection** - Compares current metrics with historical data to detect degrading trends
2. **Scheduled Automation** - Automatic report generation at set intervals with 7-day historical retention
3. **Email Notifications** - Sends immediate alerts when critical/major issues or degradation trends are detected

## What's New

### New Modules

#### 1. `src/trend_analyzer.py`
- **TrendAnalyzer class** - Manages historical report storage and trend analysis
- **Features:**
  - Stores reports in `reports/history/YYYY-MM-DD/` directory
  - Compares metrics day-over-day
  - Calculates trend indicators: ↑ (worsening), ↓ (improving), → (stable)
  - Generates human-readable trend reports
  - Automatically cleans up reports older than 7 days

**Key Methods:**
- `save_report_to_history()` - Store current report to history
- `analyze_trends()` - Compare with previous day and detect degradation
- `generate_trend_report()` - Create formatted trend analysis
- `get_history_summary()` - View stored historical data

#### 2. `src/notification_service.py`
- **NotificationService class** - Sends email alerts for critical issues
- **Features:**
  - SMTP email support (Gmail, Office365, custom servers)
  - HTML-formatted email templates
  - Different alert types: critical, major, trend degradation
  - TLS/SSL support

**Key Methods:**
- `send_critical_alert()` - Alert for critical infrastructure issues
- `send_major_alert()` - Alert for major degraded infrastructure
- `send_trend_alert()` - Alert for detected degradation trends
- `send_email()` - Send raw email with custom content

### Updated Files

#### 1. `src/report_generator.py`
- Now accepts optional `TrendAnalyzer` instance
- Saves reports to history
- Analyzes trends
- Returns report data with trend analysis results

#### 2. `src/main.py`
- Imports and initializes TrendAnalyzer and NotificationService
- Updated `run_monitoring_cycle()` to accept config parameter
- Implements notification sending on critical/major issues and trends
- Updated `run_daemon()` to pass config to monitoring cycle

#### 3. `config/config.yaml`
- Added `notifications` section with email configuration
- Added `history` section for report retention settings
- Added `thresholds` section for alert triggers

## Configuration

### Email Configuration

Edit `config/config.yaml` to enable notifications:

```yaml
notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"      # Your SMTP server
    smtp_port: 587
    use_tls: true
    smtp_user: "your-email@gmail.com"  # Your email
    smtp_password: "your-app-password" # Use app password for Gmail 2FA
    from_address: "noreply@mist-infra-manager.local"
    recipients:
      - "ops-team@example.com"
      - "on-call@example.com"
```

### Gmail Configuration Example

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use the generated 16-character password as `smtp_password`
4. Set `smtp_user` to your Gmail address
5. Set `smtp_server: "smtp.gmail.com"` and `smtp_port: 587`

### History Configuration

```yaml
history:
  directory: "reports/history"  # Where to store historical reports
  keep_days: 7                  # Keep last 7 days of reports
  auto_cleanup: true            # Automatically remove old reports
```

### Alert Thresholds

```yaml
thresholds:
  trend_degradation_percent: 5  # Alert if metrics change > 5% per day
  pre_warning_capacity: 85      # Alert before critical (70%)
  pre_warning_roaming: 95       # Alert before roaming issues
```

## Usage

### Single Run with Trend Analysis and History

```bash
python src/main.py --mode report
```

This will:
1. Generate infrastructure report
2. Store report in `reports/history/YYYY-MM-DD/`
3. Compare with previous day's report
4. Generate trend analysis
5. Send notifications if enabled and thresholds exceeded

### Daemon Mode with Automatic Monitoring

```bash
# Run monitoring every 15 minutes (from config)
python src/main.py --daemon

# Run monitoring every 10 minutes (override config)
python src/main.py --daemon --interval 10
```

### Verbose Output

```bash
python src/main.py --verbose --daemon --interval 15
```

## Alert Types

### Critical Alerts (🚨)
Sent when:
- Critical insights detected in infrastructure
- Immediate action required

**Recipients:** All configured email addresses

### Major Alerts (⚠️)
Sent when:
- Major insights detected
- Critical insights count is zero
- Action needed within 24 hours

**Recipients:** All configured email addresses

### Trend Alerts (📈)
Sent when:
- Infrastructure metrics are degrading
- Compared to previous day
- Multiple metrics show negative trends

**Recipients:** All configured email addresses

## Report Structure

```
reports/
├── history/
│   ├── 2026-01-23/
│   │   ├── HEALTH_DASHBOARD_20260123_143500.json
│   │   ├── HEALTH_DASHBOARD_20260123_153600.json
│   │   └── ...
│   ├── 2026-01-22/
│   │   ├── HEALTH_DASHBOARD_20260122_143500.json
│   │   └── ...
│   └── ...
├── HEALTH_DASHBOARD_20260123_154012.json
├── HEALTH_DASHBOARD_20260123_154012.txt
└── SUMMARY_REPORT_20260123_154012.txt
```

## Trend Analysis Output

Example trend report in logs:

```
======================================================================
TREND ANALYSIS REPORT
======================================================================

Overall Trend: ↑

⚠️  DEGRADATION DETECTED:
  • critical_insights: 2 → 3 (+50.0%) ↑
  • capacity: 72.0 → 75.0 (+4.2%) ↑

→ STABLE: 5 metric(s) stable

======================================================================
```

## Testing the Implementation

### Test Trend Analysis Without Email

Edit `config/config.yaml`:
```yaml
notifications:
  enabled: false  # Disable email
```

Run:
```bash
python src/main.py --mode report --verbose
```

Check `reports/history/` for stored reports and trend analysis in logs.

### Test Email Notifications

1. Configure valid SMTP credentials in `config/config.yaml`
2. Set `notifications.enabled: true` and `notifications.email.enabled: true`
3. Run:
   ```bash
   python src/main.py --mode report --verbose
   ```
4. Check logs for email sending confirmation
5. Verify email arrives in configured inbox

### Verify History Storage

```bash
# List history directories
ls reports/history/

# View most recent report
cat "reports/history/$(date +%Y-%m-%d)/HEALTH_DASHBOARD_*.json" | tail -1
```

## Performance Considerations

- **History Cleanup:** Runs automatically, removes reports older than `keep_days`
- **Email Sending:** Non-blocking, timeout set to 10 seconds per email
- **Memory Usage:** Reports stored as JSON, ~10KB per report
- **Storage:** ~1MB per day for a typical infrastructure (7-day retention)

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials:**
   ```bash
   python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
   ```

2. **Enable verbose logging:**
   ```bash
   python src/main.py --verbose --mode report
   ```

3. **Check logs:**
   ```bash
   tail -f mist_infra_manager.log | grep -i smtp
   ```

### Trends Not Detected

1. Ensure at least one previous report exists
2. Check `reports/history/` for historical data
3. Verify previous report contains comparable metrics
4. Check logs for trend analysis errors

### History Directory Issues

1. Verify `reports/history/` directory exists and is writable
2. Check disk space: `df reports/`
3. Verify permissions: `ls -la reports/`

## Next Phase

After this implementation is stable, consider Phase 2 features:
- Health scoring system
- Predictive thresholds (forecast time-to-critical)
- Real-time watch mode dashboard
- Baseline learning for anomaly detection

## Files Modified

- ✅ `src/trend_analyzer.py` - NEW
- ✅ `src/notification_service.py` - NEW
- ✅ `src/report_generator.py` - Updated with trend integration
- ✅ `src/main.py` - Updated with trend and notification integration
- ✅ `config/config.yaml` - Added notification and history config
- ✅ `config/config.yaml.template` - Updated with new configuration options

## Testing Checklist

- [x] All modules have no syntax errors
- [ ] Test single run with trend analysis: `python src/main.py --mode report`
- [ ] Test daemon mode: `python src/main.py --daemon --interval 5`
- [ ] Verify reports saved to `reports/history/`
- [ ] Test email notifications (if configured)
- [ ] Test history cleanup after 7+ days
- [ ] Test graceful shutdown with Ctrl+C
- [ ] Review logs: `tail -f mist_infra_manager.log`

