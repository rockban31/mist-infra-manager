# Testing Guide - Option A Implementation

## Platform Notes

**For Windows Users:** All bash commands below have PowerShell equivalents. See [Windows Testing Commands](#windows-testing-commands) section below for PowerShell versions.

## Test Environment Setup

### Prerequisites
- ✅ Python 3.9+ (you have 3.13)
- ✅ Valid Mist API credentials in `config/config.yaml`
- ✅ Internet connection for SMTP (if testing email)

## Test Plan

### Test 1: Basic Trend Analysis (No Email)
**Objective:** Verify trend analysis works without email configuration

**Steps:**
```bash
# Run with debug output
python src/main.py --mode report --verbose

# Check output for:
# - "TREND ANALYSIS REPORT"
# - "DEGRADATION DETECTED" or "STABLE: X metric(s) stable"
# - No SMTP errors
```

**Expected Results:**
- ✅ Report generated successfully
- ✅ Trend analysis appears in logs
- ✅ Report saved to `reports/history/YYYY-MM-DD/`
- ✅ No email sending (notifications disabled)

**Verification:**
```bash
# Check if history directory was created
ls -la reports/history/

# View latest report
cat reports/history/$(date +%Y-%m-%d)/HEALTH_DASHBOARD_*.json | python -m json.tool
```

**Windows PowerShell:**
```powershell
# Check if history directory was created
Get-ChildItem reports/history/ -Force

# View latest report
$date = Get-Date -Format "yyyy-MM-dd"
Get-Content "reports/history/$date/HEALTH_DASHBOARD_*.json" | python -m json.tool
```

---

### Test 2: History Retention
**Objective:** Verify 7-day history management works correctly

**Steps:**
```bash
# Run report twice to create multiple entries
python src/main.py --mode report
sleep 5
python src/main.py --mode report

# Check history contains today's reports
ls -la reports/history/$(date +%Y-%m-%d)/

# Expected: 2 or more HEALTH_DASHBOARD_*.json files
```

**Windows PowerShell:**
```powershell
# Run report twice to create multiple entries
python src/main.py --mode report
Start-Sleep -Seconds 5
python src/main.py --mode report

# Check history contains today's reports
$date = Get-Date -Format "yyyy-MM-dd"
Get-ChildItem "reports/history/$date/" -Force

# Expected: 2 or more HEALTH_DASHBOARD_*.json files
```

**Expected Results:**
- ✅ Multiple reports in today's directory
- ✅ Unique timestamps for each
- ✅ All valid JSON format

**Verification:**
```bash
# Count reports per day
find reports/history -name "HEALTH_DASHBOARD_*.json" -type f | wc -l

# Check file sizes are reasonable (should be ~10KB)
ls -lh reports/history/*/HEALTH_DASHBOARD_*.json | head -5
```

**Windows PowerShell:**
```powershell
# Count reports per day
(Get-ChildItem reports/history -Recurse -Filter "HEALTH_DASHBOARD_*.json").Count

# Check file sizes are reasonable (should be ~10KB)
Get-ChildItem reports/history -Recurse -Filter "HEALTH_DASHBOARD_*.json" | 
  Select-Object FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}} | 
  Select-Object -First 5
```

### Test 3: Trend Detection
**Objective:** Verify trend analysis detects changes

**Setup:**
```bash
# Need at least 2 reports from different days
# If you don't have yesterday's report, manually create one:
mkdir -p reports/history/$(date -d yesterday +%Y-%m-%d)
cp reports/HEALTH_DASHBOARD_*.json \
   reports/history/$(date -d yesterday +%Y-%m-%d)/HEALTH_DASHBOARD_old.json
```

**Windows PowerShell:**
```powershell
# Need at least 2 reports from different days
# If you don't have yesterday's report, manually create one:
$yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
$historyDir = "reports/history/$yesterday"
New-Item -Path $historyDir -ItemType Directory -Force
Copy-Item reports/HEALTH_DASHBOARD_*.json "$historyDir/HEALTH_DASHBOARD_old.json"
```

**Steps:**
```bash
python src/main.py --mode report --verbose

# Look in logs for trend analysis
# Should show: "Overall Trend: ↑" or "→" or "↓"
```

**Expected Results:**
- ✅ Trend analysis runs when previous day's report exists
- ✅ Shows trend indicators
- ✅ Reports any degradation detected

---

### Test 4: Email Notifications (Optional)
**Objective:** Verify email sending functionality

**Prerequisites:**
- Valid SMTP credentials
- At least one critical or major insight in your infrastructure

**Setup:**
```yaml
# Edit config/config.yaml:
notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    smtp_user: "your-test-email@gmail.com"
    smtp_password: "your-app-password"
    from_address: "noreply@test.local"
    recipients:
      - "your-test-email@gmail.com"
```

**Steps:**
```bash
# Run with verbose output
python src/main.py --mode report --verbose

# Check logs for:
# - "Sending critical alert notification..."
# - "Email sent successfully"
# - No SMTP errors

# Monitor logs in real-time
tail -f mist_infra_manager.log | grep -i email
```

**Expected Results:**
- ✅ Email sending confirmation in logs
- ✅ No SMTP errors
- ✅ Email arrives in inbox within 1-2 minutes

**Troubleshooting Email:**
```bash
# Test SMTP connection
python -c "import smtplib; s=smtplib.SMTP('exchrelay.global.tesco.org', 25); print('OK')"

# Test credentials (Tesco relay doesn't require authentication)
python << 'EOF'
import smtplib
try:
    s = smtplib.SMTP('exchrelay.global.tesco.org', 25, timeout=10)
    print('SMTP Connection: OK')
    s.quit()
except Exception as e:
    print(f'SMTP Error: {e}')
EOF
```

---

### Test 5: Daemon Mode
**Objective:** Verify continuous monitoring works

**Steps:**
```bash
# Start daemon with 2-minute interval for testing
python src/main.py --daemon --interval 2 --verbose

# Wait for 2+ cycles (4+ minutes)
# Then press Ctrl+C to stop

# Check that multiple reports were generated
ls -la reports/history/$(date +%Y-%m-%d)/
```

**Windows PowerShell:**
```powershell
# Start daemon with 2-minute interval for testing
python src/main.py --daemon --interval 2 --verbose

# Wait for 2+ cycles (4+ minutes)
# Then press Ctrl+C to stop

# Check that multiple reports were generated
$date = Get-Date -Format "yyyy-MM-dd"
Get-ChildItem "reports/history/$date/" -Force
```

**Expected Results:**
- ✅ Monitoring cycle runs every 2 minutes
- ✅ New report generated each cycle
- ✅ Graceful shutdown on Ctrl+C
- ✅ No errors in logs

**Verification:**
```bash
# Count reports generated (should be multiple)
find reports/history/$(date +%Y-%m-%d) -name "*.json" | wc -l

# Check log entries per cycle
grep "Starting monitoring cycle" mist_infra_manager.log | tail -5
```

**Windows PowerShell:**
```powershell
# Count reports generated (should be multiple)
$date = Get-Date -Format "yyyy-MM-dd"
(Get-ChildItem "reports/history/$date" -Filter "*.json").Count

# Check log entries per cycle
Get-Content mist_infra_manager.log | Select-String "Starting monitoring cycle" | Select-Object -Last 5
```

---

### Test 6: Graceful Shutdown
**Objective:** Verify daemon mode shuts down cleanly

**Steps:**
```bash
# Start daemon
python src/main.py --daemon --interval 2

# Wait for cycle to start
# Press Ctrl+C

# Verify clean shutdown
# Check last log line shows shutdown message
```

**Expected Results:**
- ✅ Application responds to Ctrl+C
- ✅ Log shows "Daemon shutdown complete"
- ✅ No zombie processes

**Verification:**
```bash
# Check for any remaining Python processes
ps aux | grep "python.*main.py" | grep -v grep

# Should return no results (clean shutdown)
```

### Test 7: Configuration Validation
**Objective:** Verify configuration loading works correctly

**Steps:**
```bash
# Test with missing config
python src/main.py --config /nonexistent/path.yaml

# Should show error about config file

# Test with valid config
python src/main.py --config config/config.yaml --mode report

# Should work normally
```

**Expected Results:**
- ✅ Proper error on missing config
- ✅ Works with valid config path
- ✅ Defaults used for optional settings

---

### Test 8: Command Line Arguments
**Objective:** Verify all CLI options work

**Steps:**
```bash
# Test all modes
python src/main.py --mode monitor
python src/main.py --mode insights
python src/main.py --mode report
python src/main.py --mode all

# Test verbose flag
python src/main.py --verbose --mode report

# Test interval override
python src/main.py --daemon --interval 5
# (Stop with Ctrl+C after 10+ minutes)
```

**Expected Results:**
- ✅ All modes execute successfully
- ✅ Verbose output shows more details
- ✅ Interval setting works correctly

---

## Integration Tests

### Test 9: End-to-End Workflow
**Objective:** Complete workflow from API call to notifications

**Scenario:** Simulate a degraded infrastructure scenario

**Steps:**
```bash
# 1. Generate baseline report
python src/main.py --mode report
sleep 60

# 2. (In infrastructure) Intentionally degrade some metric or create insight
# (Wait for Mist API to reflect changes)

# 3. Generate second report
python src/main.py --mode report --verbose

# 4. Check for:
# - Trend detection (↑ ↓ →)
# - Degradation alerts if enabled
# - Email sent if configured
```

**Expected Results:**
- ✅ Trend analysis shows degradation
- ✅ Appropriate alerts generated
- ✅ Notifications sent (if enabled)
- ✅ Everything logged correctly

---

## Performance Tests

### Test 10: Resource Usage
**Objective:** Monitor memory and CPU usage during operations

**Steps:**
```bash
# Start daemon and monitor
python src/main.py --daemon --interval 1 &
DAEMON_PID=$!

# Monitor for 2 minutes
watch -n 1 "ps -p $DAEMON_PID -o %cpu,%mem,vsz,rss"

# Kill daemon
kill $DAEMON_PID
```

**Expected Results:**
- ✅ CPU usage < 5% during idle
- ✅ Memory < 50MB base usage
- ✅ No memory leaks over time
- ✅ Clean shutdown

---

## Checklist for Production Deployment

### Pre-Deployment Tests
- [ ] Test 1: Basic Trend Analysis - PASS
- [ ] Test 2: History Retention - PASS
- [ ] Test 3: Trend Detection - PASS
- [ ] Test 4: Email Notifications - PASS (if using)
- [ ] Test 5: Daemon Mode - PASS
- [ ] Test 6: Graceful Shutdown - PASS
- [ ] Test 7: Configuration Validation - PASS
- [ ] Test 8: CLI Arguments - PASS
- [ ] Test 9: End-to-End Workflow - PASS
- [ ] Test 10: Resource Usage - PASS

### Configuration Checklist
- [ ] API token configured in `config/config.yaml`
- [ ] Email credentials configured (if using)
- [ ] History directory exists and is writable
- [ ] Retention period set appropriately (7 days default)
- [ ] Notification recipients configured correctly
- [ ] SMTP server and port correct for your provider

### Production Readiness
- [ ] Logs are readable and informative
- [ ] Error messages are helpful
- [ ] No sensitive data in logs
- [ ] Documentation complete
- [ ] Runbook created for common issues
- [ ] Backup plan for email failures

---

## Test Results Template

```markdown
# Test Results - Option A Implementation
Date: YYYY-MM-DD
Tester: [Name]

## Basic Tests
- [ ] Test 1: Trend Analysis - Result: PASS/FAIL
- [ ] Test 2: History Retention - Result: PASS/FAIL
- [ ] Test 3: Trend Detection - Result: PASS/FAIL
- [ ] Test 4: Email Notifications - Result: PASS/FAIL (if applicable)

## Integration Tests
- [ ] Test 5: Daemon Mode - Result: PASS/FAIL
- [ ] Test 6: Graceful Shutdown - Result: PASS/FAIL
- [ ] Test 7: Configuration - Result: PASS/FAIL
- [ ] Test 8: CLI Arguments - Result: PASS/FAIL
- [ ] Test 9: End-to-End - Result: PASS/FAIL

## Performance Tests
- [ ] Test 10: Resource Usage - Result: PASS/FAIL

## Notes
[Any issues or observations]

## Sign-off
- Tester: [Signature]
- Date: YYYY-MM-DD
- Status: [Ready for Production / Needs Work]
```

---

## Quick Test Commands

Copy-paste ready commands for rapid testing:

```bash
# Full test suite (requires ~15-20 minutes)
echo "=== Test 1: Basic Analysis ===" && \
python src/main.py --mode report --verbose && \
echo "=== Test 2: History Check ===" && \
ls -la reports/history/$(date +%Y-%m-%d)/ && \
echo "=== Test 5: Daemon Test (2 cycles) ===" && \
timeout 120 python src/main.py --daemon --interval 1 || true && \
echo "=== Tests Complete ===" && \
ls -la reports/history/$(date +%Y-%m-%d)/ | tail -5
```

---

For any test failures, check:
1. Logs: `tail -100 mist_infra_manager.log`
2. Configuration: `cat config/config.yaml`
3. API connectivity: Verify API token and network access
4. SMTP connectivity: Verify SMTP credentials and firewall rules

---

## Windows Testing Commands

If you're using Windows PowerShell, use these commands instead of the bash equivalents above:

### Quick Test Commands (PowerShell)

```powershell
# Full test suite (requires ~15-20 minutes)
Write-Host "=== Test 1: Basic Analysis ===" ; `
python src/main.py --mode report --verbose ; `
Write-Host "=== Test 2: History Check ===" ; `
$date = Get-Date -Format "yyyy-MM-dd" ; `
Get-ChildItem "reports/history/$date/" -Force ; `
Write-Host "=== Test 5: Daemon Test (2 cycles) ===" ; `
Start-Process python -ArgumentList "src/main.py", "--daemon", "--interval", "1" -Wait -NoNewWindow ; `
Write-Host "=== Tests Complete ===" ; `
Get-ChildItem "reports/history/$date/" -Force | Select-Object -Last 5
```

### Common Command Translations

| Bash | PowerShell |
|------|-----------|
| `ls -la dir/` | `Get-ChildItem dir/ -Force` |
| `cat file.txt` | `Get-Content file.txt` |
| `tail -f file.txt` | `Get-Content file.txt -Wait` |
| `tail -n 100 file.txt` | `Get-Content file.txt -Tail 100` |
| `grep "pattern" file.txt` | `Get-Content file.txt \| Select-String "pattern"` |
| `mkdir -p dir/` | `New-Item -Path dir/ -ItemType Directory -Force` |
| `cp source dest` | `Copy-Item source dest` |
| `sleep 5` | `Start-Sleep -Seconds 5` |
| `find dir -name "*.json"` | `Get-ChildItem dir -Recurse -Filter "*.json"` |
| `wc -l file.txt` | `(Get-Content file.txt \| Measure-Object -Line).Lines` |

### Test Failures Troubleshooting (PowerShell)

```powershell
# Check logs
Get-Content mist_infra_manager.log -Tail 100

# View configuration
Get-Content config/config.yaml

# Count reports generated
$date = Get-Date -Format "yyyy-MM-dd"
(Get-ChildItem "reports/history/$date" -Filter "*.json").Count

# Search logs for errors
Get-Content mist_infra_manager.log | Select-String "ERROR|CRITICAL"

# Check processes
Get-Process python | Where-Object {$_.CommandLine -like "*main.py*"}
```
