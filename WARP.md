# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
Mist Infrastructure Manager is a proactive infrastructure management tool for Juniper Mist networks. It monitors Service Level Expectations (SLE), analyzes insights, and provides actionable recommendations for network infrastructure health via the Mist API.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Configuration Setup
```bash
# Copy template and edit with your Mist API token
cp config/config.yaml.template config/config.yaml
```

### Running the Application
```bash
# Run all monitoring and analysis (default)
python src/main.py

# Monitor SLE metrics only
python src/main.py --mode monitor

# Analyze insights only
python src/main.py --mode insights

# Generate reports
python src/main.py --mode report

# Enable verbose logging
python src/main.py --verbose

# Use custom configuration file
python src/main.py --config /path/to/config.yaml
```

### Testing
Note: The tests directory currently exists but is empty. When adding tests:
- Use pytest as the testing framework (standard for Python projects)
- Run tests with: `pytest tests/`
- For a single test file: `pytest tests/test_filename.py`

## Architecture

### Core Components
The application follows a modular architecture with three main components that interact with a central API client:

**MistAPIClient** (`src/mist_client.py`)
- Central API client handling all communication with Juniper Mist API
- Manages authentication via API token from config file
- Auto-initializes organization ID on startup
- Provides methods for retrieving sites, devices, SLE metrics, insights, and alarms
- Uses requests.Session for connection pooling

**SLEMonitor** (`src/sle_monitor.py`)
- Monitors Service Level Expectations across all sites
- Compares metrics against configurable thresholds (successful_connect, time_to_connect, throughput, capacity, roaming)
- Default thresholds defined in `THRESHOLDS` class constant
- Generates warnings when metrics fall below thresholds
- Can produce summary statistics across sites

**InsightsAnalyzer** (`src/insights_analyzer.py`)
- Analyzes Mist platform insights from the organization
- Categorizes insights by severity (critical, major, minor, warning, info), type, and site
- Generates detailed reports on critical and major insights
- Provides proactive recommendations based on patterns (e.g., multiple insights of same type, site-specific issues)
- Uses severity levels for prioritization

### Data Flow
1. `main.py` initializes MistAPIClient with config
2. MistAPIClient authenticates and retrieves org_id from `/self` endpoint
3. Based on mode flag, main.py instantiates SLEMonitor and/or InsightsAnalyzer
4. Monitors/analyzers call MistAPIClient methods to fetch data
5. Each component processes data and logs findings
6. All output goes to both console and `mist_infra_manager.log`

### Configuration
Configuration is managed via YAML (`config/config.yaml`):
- Required: `mist.api_token` - Mist API authentication token
- Optional: `sle_thresholds` - Custom thresholds for SLE monitoring
- Optional: `monitoring` - Intervals and feature toggles

**IMPORTANT**: `config/config.yaml` is gitignored and contains sensitive API tokens. Always use `config.yaml.template` as a reference.

## API Integration

### Mist API Details
- Base URL: `https://api.mist.com/api/v1`
- Authentication: Token-based via Authorization header
- Rate limit: 5000 requests/hour per organization
- Key endpoints used:
  - `/self` - Get user info and organization privileges
  - `/orgs/{org_id}/sites` - List all sites
  - `/sites/{site_id}/sle` - Get SLE metrics for a site
  - `/orgs/{org_id}/insights` - Get organizational insights
  - `/sites/{site_id}/devices` - Get devices for a site

### API Token Security
- Never commit actual API tokens to version control
- Tokens should be obtained from: https://manage.mist.com → Organization → Settings → API Tokens
- In production, consider using environment variables instead of config files
- Rotate tokens regularly per security best practices

## Code Style and Patterns

### Logging
- All modules use Python's `logging` module
- Logger obtained via `logging.getLogger(__name__)`
- Log levels: DEBUG (verbose), INFO (default), WARNING (issues/violations), ERROR (failures)
- Output to both file (`mist_infra_manager.log`) and console

### Error Handling
- API calls wrapped in try/except blocks
- Requests use `response.raise_for_status()` to catch HTTP errors
- Errors logged with context before re-raising or returning
- Top-level exception handling in `main.py` with `exc_info=True` for stack traces

### Type Hints
- Functions use type hints for parameters and return values
- Common types: `Dict`, `List`, `Optional` from typing module
- Helps with code clarity and IDE support

## Windows-Specific Considerations
- Use PowerShell path separators when working with file paths
- Example paths use backslashes: `D:\mist-infra-manager\src\main.py`
- Python handles both forward and backslashes, but prefer native format in docs
