# Mist Infrastructure Manager

Proactive infrastructure monitoring tool for Juniper Mist wireless networks. Monitors SLE (Service Level Expectation) metrics across sites, generates health reports, and sends automated email alerts with detailed classifier breakdowns.

## Features

- **SLE Monitoring** — Tracks 7 SLE metrics across all sites: Capacity, Roaming, Time to Connect, Successful Connect, AP Health, Throughput, Coverage
- **Classifier Breakdown** — Extracts per-classifier degradation data from each SLE metric (e.g., DHCP, Association, Weak Signal) with % degraded and impact counts
- **Severity Classification** — Auto-classifies insights as Critical (<70%), Major (<80%), Warning (<90%), or Info (≥90%)
- **HTML Email Alerts** — Sends grouped SLE classifier tables in email body with color-coded severity and per-classifier columns
- **Reports** — Generates summary reports (`.txt`) and health dashboards (`.json`) per run
- **Trend Analysis** — Compares day-over-day metrics to detect degradation, with 7-day rolling history
- **Daemon Mode** — Continuous monitoring with configurable interval (default: 15 minutes)

## Monitored SLE Metrics & Classifiers

| SLE Metric | Classifiers |
|---|---|
| **Time to Connect** | Association, Authorization, DHCP Nack, DHCP Stuck, DHCP Unresponsive, IP-Services |
| **Successful Connects** | Association, Authorization, DNS, DHCP Incomplete, DHCP Nack, DHCP Discover Unresponsive, DHCP Renew Unresponsive, ARP |
| **Coverage** | Weak Signal, Asymmetry Downlink, Asymmetry Uplink |
| **Roaming** | Latency Slow Standard Roam, Latency Slow 11r Roam, Latency Slow OKC Roam, Stability Failed to Fast Roam, Signal Quality Suboptimal Roam, Signal Quality Sticky Client, Signal Quality Interband Roam |
| **Throughput** | Network Issues, Coverage, Device Capability, Capacity Non-WiFi Interference, Capacity WiFi Interference, Capacity Excessive Client Load, Capacity High Bandwidth Utilization |
| **Capacity** | Non-WiFi Interference, WiFi Interference, Client Usage, Client Count |
| **AP Health** | Low Power, AP Disconnected AP Reboot, AP Disconnected AP Unreachable, AP Disconnected Switch Down, AP Disconnected Site Down, Ethernet Errors, Speed Mismatch, Network Jitter, Network Latency, Network Tunnel Down |

## Prerequisites

- Python 3.9+
- Juniper Mist API token (EU endpoint: `api.eu.mist.com`)
- SMTP server access for email notifications

## Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure
cp config/config.yaml.template config/config.yaml
# Edit config/config.yaml with your API token and SMTP settings
```

## Usage

```bash
# Single report with email alert
python src/main.py --mode report

# Continuous monitoring (every 15 minutes)
python src/main.py --daemon --interval 15

# All modes (monitor + insights + report)
python src/main.py --mode all

# Verbose logging
python src/main.py --mode report --verbose
```

### CLI Options

| Option | Description |
|---|---|
| `--mode {monitor,insights,report,all}` | Operation mode (default: `all`) |
| `--daemon` | Run continuously with scheduled intervals |
| `--interval MINUTES` | Monitoring interval in daemon mode |
| `--config PATH` | Config file path (default: `config/config.yaml`) |
| `--verbose` | Enable debug logging |

## Configuration

Edit `config/config.yaml` (create from template):

```yaml
mist:
  api_token: "YOUR_API_TOKEN"

notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: "exchrelay.global.tesco.org"
    smtp_port: 25
    use_tls: false
    from_address: "mist-infra-manager@company.com"
    recipients:
      - "ops@company.com"

history:
  directory: "reports/history"
  keep_days: 7
```

### Getting Your API Token

1. Log in to https://manage.mist.com
2. Go to Organization > Settings > API Tokens
3. Create a new token with read permissions
4. Add to `config/config.yaml`

## Project Structure

```
mist-infra-manager/
├── src/
│   ├── main.py                 # Entry point, CLI, orchestration
│   ├── mist_client.py          # Mist REST API client
│   ├── report_generator.py     # Reports, health dashboards, SLE classifier tables
│   ├── notification_service.py # HTML email alerts (SMTP)
│   ├── sle_monitor.py          # Standalone SLE metric monitoring
│   ├── insights_analyzer.py    # Insights analysis module
│   ├── trend_analyzer.py       # Day-over-day trend comparison
│   └── __init__.py
├── config/
│   ├── config.yaml             # Active config (git-ignored)
│   └── config.yaml.template    # Config template
├── reports/                    # Generated reports (git-ignored)
│   └── history/                # Rolling 7-day history for trend analysis
├── bruno/                      # Bruno API collection (10 endpoints)
├── requirements.txt            # requests, PyYAML, schedule
├── .gitignore
└── README.md
```

## Output

Each run generates:

- `SUMMARY_REPORT_<timestamp>.txt` — Priority-sorted insights with site details
- `HEALTH_DASHBOARD_<timestamp>.txt` — Status dashboard with action recommendations
- `HEALTH_DASHBOARD_<timestamp>.json` — Machine-readable health data
- `reports/history/<date>/` — Historical snapshots for trend analysis

## Email Alerts

Alerts are triggered based on severity:

- **Critical alert** — 1+ critical insights detected
- **Major alert** — 1+ major insights (no critical)
- **Trend alert** — Day-over-day degradation detected

Each email contains:
- Infrastructure health summary with site status grid
- **SLE Classifier Breakdown** — 7 grouped tables (one per SLE metric) with per-site classifier columns showing `% degraded, users=N, aps=N`
- Summary report as attachment

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/self` | Organization discovery |
| `GET /api/v1/orgs/{org}/sites` | List sites |
| `GET /api/v1/orgs/{org}/insights/sites-sle` | Org-level SLE insights |
| `GET /api/v1/sites/{site}/sle/site/{site}/metric/{metric}/summary` | Per-metric classifier summary |

## Logging

- **Console** — Formatted real-time output
- **File** — `mist_infra_manager.log` (debug level, git-ignored)

```powershell
Get-Content mist_infra_manager.log -Tail 50
```
