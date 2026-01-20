# Mist Infrastructure Manager - Proactive Enhancement Roadmap

## Current State (Reactive)
- ✅ Monitors current metrics
- ✅ Reports existing issues
- ✅ Alert priority system
- ❌ No prediction of future problems
- ❌ No automatic alerts/escalations
- ❌ No trend comparison

---

## Strategy: Making the System Proactive

### Phase 1: Quick Wins (Easy to Implement)

#### 1. **Trend Analysis & Degradation Detection**
   - Compare metrics with previous runs
   - Alert if metrics are getting worse
   - Store historical snapshots (daily/weekly)
   - Example: "Capacity was 75% yesterday, now 79% - trending upward ⬆️"
   
   **Implementation Steps:**
   - Store last 7 days of reports in `reports/history/` directory
   - Compare current metrics with previous day
   - Generate trend indicators: ↑ (worsening), ↓ (improving), → (stable)
   - Add trend section to summary report

#### 2. **Scheduled Automation**
   - Automatic report generation at set intervals
   - Store historical data automatically
   - Track trends automatically
   
   **Implementation Steps:**
   - Use existing daemon mode `--daemon --interval X`
   - Automatically keep only last 7 days of reports
   - Create archive directory for older reports
   - Add timestamp-based cleanup logic

#### 3. **Email/Slack Notifications** (Immediate Alerts)
   - Alert immediately when critical issues detected
   - Don't wait for scheduled reports
   - Route to on-call teams
   
   **Implementation Steps:**
   - Add email configuration to `config/config.yaml`
   - Send email notification when critical/major issues detected
   - Include direct links to dashboard and remediation steps
   - Optional: Slack webhook integration

---

### Phase 2: Medium Effort Enhancements

#### 4. **Predictive Thresholds**
   - Alert when approaching critical (not just at critical)
   - Example: "Warning approaching critical in 2-3 days at current trend"
   - Set pre-warning thresholds
   
   **Implementation Steps:**
   - Calculate trend velocity (% change per day)
   - Estimate days until critical threshold reached
   - Create pre-warning alerts for trending issues
   - Add forecast section to reports

#### 5. **Health Scoring System**
   - Assign health score to each site (0-100)
   - Track score trends over time
   - Identify at-risk sites before failures
   
   **Implementation Steps:**
   - Calculate composite score: average of all metrics
   - Weight by severity: critical=10%, major=20%, warning=30%
   - Track daily scores over time
   - Alert when score drops > 10 points/day
   - Display score trends in dashboard

#### 6. **Real-Time Dashboard (Watch Mode)**
   - Live monitoring display instead of static reports
   - Auto-refresh every 5-15 seconds
   - Visual indicators for status changes
   - Show recent changes highlighted
   
   **Implementation Steps:**
   - Create terminal-based live dashboard using `curses` or similar
   - Implement `--watch` or `--live` mode
   - Show live metrics updates
   - Highlight newly degraded sites

#### 7. **Baseline Learning**
   - Establish what "normal" looks like for each site
   - Alert on significant deviations from baseline
   - Detect seasonal patterns
   
   **Implementation Steps:**
   - Store 30-day baseline for each metric per site
   - Calculate standard deviation for each metric
   - Alert when metrics deviate > 2σ (standard deviations)
   - Build weekly baseline for day-of-week patterns

---

### Phase 3: Advanced Features (Complex)

#### 8. **Automatic Escalation & Ticketing**
   - Auto-create tickets for critical issues
   - Integrate with ticketing systems (Jira, ServiceNow)
   - Page on-call engineer if not resolved within X minutes
   - Update ticket status based on resolution
   
   **Implementation Steps:**
   - Add Jira/ServiceNow API integration
   - Create ticket template for each severity level
   - Track ticket lifecycle
   - Implement escalation timer

#### 9. **Machine Learning Prediction**
   - Predict failures before they happen
   - Anomaly detection for unusual patterns
   - Estimate time-to-failure for degrading metrics
   
   **Implementation Steps:**
   - Use isolation forest for anomaly detection
   - Train model on historical data
   - Implement ARIMA for time-series forecasting
   - Alert on predicted issues

#### 10. **Multi-Site Correlation Analysis**
   - Identify if issues correlate across sites
   - Detect infrastructure-wide problems vs site-specific
   - Alert on related failures
   
   **Implementation Steps:**
   - Analyze cross-site metric correlations
   - Detect when multiple sites degrade simultaneously
   - Identify root cause patterns
   - Alert on infrastructure-wide issues

---

## Implementation Priority Recommendation

### **Recommended First Implementation: Option A**
**Trend Analysis + Degradation Detection + Scheduled Automation**

**Why?**
- ✅ Easiest to implement (1-2 days)
- ✅ Provides immediate value (see trends)
- ✅ Foundation for all future features
- ✅ No external dependencies needed
- ✅ Leverages existing data collection

**Expected Outcome:**
```
Site Sonic Health Trend (Last 7 Days):
  Day 1: Capacity 72% → Status: DEGRADED
  Day 2: Capacity 73% → Status: DEGRADED ↑ (getting worse)
  Day 3: Capacity 75% → Status: DEGRADED ↑ (getting worse)
  Day 4: Capacity 79% → Status: CRITICAL ↑ ALERT: trending to critical!
```

### **Second Implementation: Option B**
**Email/Slack Notifications + Health Scoring**

**Why?**
- ✅ Enables real-time alerts
- ✅ Proactive team engagement
- ✅ Measurable health metrics
- ✅ Medium complexity

### **Third Implementation: Option C**
**Real-Time Watch Mode Dashboard**

**Why?**
- ✅ Live visibility for operations teams
- ✅ No need to wait for reports
- ✅ Immediate status awareness

---

## File Structure for Implementation

```
mist-infra-manager/
├── src/
│   ├── trend_analyzer.py        # NEW: Compare metrics over time
│   ├── notification_service.py  # NEW: Email/Slack alerts
│   ├── health_scorer.py         # NEW: Calculate health scores
│   ├── watch_mode.py            # NEW: Real-time dashboard
│   └── ... (existing files)
├── reports/
│   ├── history/                 # NEW: Store last 7 days
│   │   ├── 2026-01-20/
│   │   ├── 2026-01-19/
│   │   └── ...
│   └── ... (latest reports)
├── config/
│   ├── config.yaml.template     # ADD: email/notification settings
│   └── config.yaml              # gitignored
└── NEXT_PLAN.md                 # THIS FILE
```

---

## Configuration Additions Needed

```yaml
# Add to config.yaml for proactive features

notifications:
  enabled: false
  email:
    enabled: false
    recipients:
      - ops-team@example.com
    smtp_server: smtp.gmail.com
    smtp_port: 587
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/..."

thresholds:
  pre_warning_capacity: 85        # Alert before 70% critical
  pre_warning_roaming: 95
  trend_degradation_percent: 5    # Alert if trend > 5% per day
  forecast_days: 3                # Predict issues in next 3 days

history:
  keep_days: 7                    # Store last 7 days
  auto_archive: true
  archive_after_days: 30
```

---

## Quick Start for Option A (Recommended)

1. **Install dependencies:**
   ```bash
   pip install pandas scipy
   ```

2. **Create trend analyzer module** (`src/trend_analyzer.py`)
   - Load previous report
   - Compare metrics
   - Calculate trend direction
   - Generate trend report

3. **Create history storage**
   - Organize by date: `reports/history/YYYY-MM-DD/`
   - Auto-cleanup old reports
   - Keep rolling 7-day window

4. **Update report generator**
   - Compare with previous day
   - Add trend indicators
   - Show degradation alerts
   - Display forecast warnings

5. **Test with daemon mode**
   ```bash
   python src/main.py --daemon --interval 15
   ```

---

## Success Metrics

After implementation, measure:
- ⏱️ **Mean Time to Detection (MTTD)**: Time from issue start to detection
- 📉 **False Positive Rate**: Unnecessary alerts
- 🎯 **Issue Prevention Rate**: Problems caught before critical
- ⚡ **Response Time**: Time from alert to action
- 📊 **Trend Accuracy**: Forecast vs actual outcomes

---

## Questions for Implementation

1. **Which option do you want to start with?**
   - Option A: Trend Analysis (Recommended)
   - Option B: Email Notifications
   - Option C: Live Dashboard

2. **What's your preferred notification method?**
   - Email
   - Slack
   - Both

3. **How long should we keep historical data?**
   - 7 days (recommended)
   - 30 days
   - 90 days

4. **Target timeline?**
   - This week
   - Next 2 weeks
   - Next month

---

**Next Step:** Choose an option and we'll implement it!
