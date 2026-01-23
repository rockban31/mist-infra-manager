# Quick Start Guide - Option A Implementation

## 5-Minute Setup

### Step 1: Enable Trend Analysis (No Configuration Needed)

Trend analysis is **enabled by default** and requires no configuration!

```bash
python src/main.py --mode report
```

This will:
- Generate infrastructure report
- Analyze trends vs previous day
- Store report in `reports/history/YYYY-MM-DD/`
- Display trend analysis in logs

### Step 2: Enable Email Notifications (Optional)

**For Gmail:**

1. Go to https://myaccount.google.com/apppasswords
2. Create app password (16 characters)
3. Edit `config/config.yaml`:

```yaml
notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    smtp_user: "your-email@gmail.com"
    smtp_password: "xxxx xxxx xxxx xxxx"  # 16-char app password
    from_address: "noreply@mist-infra-manager.local"
    recipients:
      - "ops-team@example.com"
```

4. Test:
```bash
python src/main.py --mode report --verbose
```

### Step 3: Enable Daemon Mode

Run continuous monitoring every 15 minutes:

```bash
python src/main.py --daemon
```

Or every 5 minutes:

```bash
python src/main.py --daemon --interval 5
```

Stop with `Ctrl+C`

## What Gets Sent

### Trend Analysis (Always Available)
- Daily degradation detection
- Metric trend indicators: ↑ ↓ →
- Change percentages
- Stored for 7 days

### Critical Alert 🚨
Sent when:
- Critical infrastructure issues detected
- Email contains affected count and remediation links

### Major Alert ⚠️
Sent when:
- Major issues detected (but not critical)
- Email includes action recommendations

### Trend Alert 📈
Sent when:
- Infrastructure degrading compared to yesterday
- Lists affected metrics with change percentages

## File Structure Created

```
reports/
├── history/
│   ├── 2026-01-23/
│   │   └── HEALTH_DASHBOARD_*.json
│   ├── 2026-01-22/
│   │   └── HEALTH_DASHBOARD_*.json
│   └── ...
├── HEALTH_DASHBOARD_*.json (latest)
├── HEALTH_DASHBOARD_*.txt (latest)
└── SUMMARY_REPORT_*.txt (latest)
```

## Verify It's Working

### Check Trend Analysis
```bash
python src/main.py --mode report --verbose
# Look for "TREND ANALYSIS REPORT" in console output
```

### Check History Storage
```bash
ls -la reports/history/
# Should show date directories like: 2026-01-23/
```

### Check Email (If Enabled)
```bash
tail -f mist_infra_manager.log | grep -i email
# Should show "Email sent successfully"
```

## Configuration Reference

### For Different Email Providers

**Office365/Outlook:**
```yaml
smtp_server: "smtp.office365.com"
smtp_port: 587
use_tls: true
```

**Generic (SendGrid, etc):**
```yaml
smtp_server: "your.smtp.server"
smtp_port: 587
use_tls: true
smtp_user: "your-username"
smtp_password: "your-password"
```

### History Retention

```yaml
history:
  directory: "reports/history"
  keep_days: 7        # Change to 30 for monthly retention
  auto_cleanup: true  # Set to false to disable auto-cleanup
```

## Common Commands

```bash
# Single report with trends
python src/main.py --mode report

# Verbose output for debugging
python src/main.py --mode report --verbose

# Daemon mode (runs in background)
python src/main.py --daemon

# Daemon with custom interval (in minutes)
python src/main.py --daemon --interval 10

# Stop daemon mode
Ctrl+C

# View logs
tail -f mist_infra_manager.log

# Check history
ls reports/history/

# View latest report
cat reports/history/$(date +%Y-%m-%d)/HEALTH_DASHBOARD_*.json | tail -1
```

## Troubleshooting

### Email Not Working?

1. **Check credentials:**
   - Verify SMTP user and password are correct
   - For Gmail, use app password (not your regular password)

2. **Check network:**
   - Verify SMTP server is reachable
   - Check firewall isn't blocking port 587

3. **Check logs:**
   ```bash
   python src/main.py --verbose 2>&1 | grep -i smtp
   ```

### Trends Not Showing?

1. Run report twice (need at least 2 reports for comparison)
2. Check `reports/history/` exists and has reports
3. Reports must be from different days for trend analysis

### Low Disk Space?

Change retention:
```yaml
history:
  keep_days: 3  # Keep only 3 days instead of 7
```

Or disable auto-storage:
```yaml
history:
  directory: ""  # Empty to disable history
```

## Next Steps After Setup

1. ✅ Run initial report: `python src/main.py --mode report`
2. ✅ Wait 24 hours for first trend comparison
3. ✅ Configure email if desired
4. ✅ Start daemon mode: `python src/main.py --daemon`
5. ✅ Monitor logs: `tail -f mist_infra_manager.log`

## Need Help?

Check these files:
- **Implementation details:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Full roadmap:** [NEXT_PLAN.md](NEXT_PLAN.md)
- **Project overview:** [README.md](README.md)
- **API documentation:** [bruno/API_QUICK_REFERENCE.md](bruno/API_QUICK_REFERENCE.md)
