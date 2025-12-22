# Mist API Bruno Collection

This directory contains a complete Bruno API collection for testing all Mist Infrastructure Manager API endpoints.

## 📋 API Endpoints Overview

This project uses the following **10 API endpoints** from Juniper Mist API v1:

| # | Endpoint | Method | Purpose | Status |
|---|----------|--------|---------|--------|
| 1 | `/self` | GET | Get user info & org ID | ✅ Works |
| 2 | `/orgs/{org_id}/sites` | GET | List all sites | ✅ Works |
| 3 | `/orgs/{org_id}/devices` | GET | List all org devices | ✅ Works |
| 4 | `/sites/{site_id}/devices` | GET | List site devices | ✅ Works |
| 5 | `/sites/{site_id}/sle/site/{site_id}/metrics` | GET | Available SLE metrics | ✅ Works |
| 6 | `/sites/{site_id}/sle/site/{site_id}/metric/{metric}/summary` | GET | SLE metric details | ✅ Works |
| 7 | `/orgs/{org_id}/insights/sites-sle` | GET | Org-level insights | ✅ Works (Fixed) |
| 8 | `/sites/{site_id}/insights/site/{site_id}/stats` | GET | Site-level insights | ✅ Works (Fixed) |
| 9 | `/orgs/{org_id}/alarms` | GET | Org-level alarms | ⚠️ May 404* |
| 10 | `/sites/{site_id}/alarms` | GET | Site-level alarms | ⚠️ May 404* |

\* *Alarms endpoints may return 404 if not enabled for your organization*

## 🚀 Getting Started

### 1. Install Bruno

Download Bruno from: https://www.usebruno.com/

### 2. Open Collection

1. Open Bruno
2. Click **"Open Collection"**
3. Navigate to: `d:\coding related\mist-infra-manager\bruno`
4. Select the folder

### 3. Configure Variables

Edit the collection variables in `Mist API Collection.bru`:

```
vars {
  base_url: https://api.eu.mist.com/api/v1
  api_token: YOUR_API_TOKEN_HERE
  org_id: YOUR_ORG_ID_HERE
  site_id: YOUR_SITE_ID_HERE
}
```

#### How to Get Your Values:

**API Token:**
1. Log in to Mist Portal: https://manage.mist.com
2. Go to **Organization → Settings → API Tokens**
3. Create a new token or copy existing one

**Org ID & Site ID:**
1. Run request `1. Get Self` first
2. Copy the `org_id` from the response
3. Run request `2. Get Sites`
4. Copy a `site_id` from the response

### 4. Update Base URL (if needed)

The default base URL is for **EU region**: `https://api.eu.mist.com/api/v1`

For other regions, update to:
- **Global 01**: `https://api.mist.com/api/v1`
- **Global 02**: `https://api.gc1.mist.com/api/v1`
- **Global 03**: `https://api.ac2.mist.com/api/v1`
- **Global 04**: `https://api.gc2.mist.com/api/v1`

## 📖 API Request Sequence

Follow this order for best results:

### Initial Setup
1. **Get Self** - Get your org_id
2. **Get Sites** - Get site_id values

### Device Information
3. **Get Devices (All Org)** - See all devices
4. **Get Devices (By Site)** - Filter by site

### SLE Metrics
5. **Get SLE Metrics (Available)** - See what metrics are available
6. **Get SLE Metric Summary** - Get detailed metric data

### Insights & Monitoring
7. **Get Insights (Org Level)** - Organization-wide insights ✅ FIXED
8. **Get Insights (Site Level)** - Site-specific insights ✅ FIXED

### Alarms (Optional)
9. **Get Alarms (Org Level)** - Organization alarms
10. **Get Alarms (Site Level)** - Site alarms

## 🔧 Common Parameters

### Time Range Calculation

For SLE metrics, you need Unix timestamps:

```python
import time

# Current time
end_time = int(time.time())

# 24 hours ago
start_time = end_time - (24 * 3600)

# 7 days ago
start_time = end_time - (7 * 24 * 3600)
```

**Online converter:** https://www.unixtimestamp.com/

### Common SLE Metrics

Available metrics you can query:
- `coverage` - WiFi coverage quality
- `capacity` - Network capacity
- `time-to-connect` - Client connection time
- `failed-to-connect` - Connection failures
- `throughput` - Network throughput
- `roaming` - Client roaming performance
- `ap-availability` - AP availability
- `ap-health` - AP health status
- `switch-health` - Switch health
- `gateway-health` - Gateway health

## ✅ Fixed Endpoints

These endpoints were **corrected** from the original implementation:

### ❌ Old (404 Error):
```
GET /orgs/{org_id}/insights
GET /sites/{site_id}/insights
```

### ✅ New (Working):
```
GET /orgs/{org_id}/insights/sites-sle
GET /sites/{site_id}/insights/site/{site_id}/stats
```

## 📝 Authentication

All requests require:

```http
Authorization: Token YOUR_API_TOKEN
Content-Type: application/json
```

## 🐛 Troubleshooting

### 404 Not Found
- Check your `org_id` and `site_id` are correct
- Some endpoints may not be available for your organization
- Verify you're using the correct base URL for your region

### 401 Unauthorized
- Verify your API token is valid
- Check token has appropriate permissions
- Token may have expired - generate a new one

### 403 Forbidden
- Your user role may not have access to this resource
- Check organization permissions

## 📚 Additional Resources

- **Mist API Documentation**: https://api.mist.com/api/v1/docs/
- **Mist Support**: https://www.juniper.net/support/
- **Bruno Documentation**: https://docs.usebruno.com/

## 🔗 Related Files

- `INSIGHTS_FIX_REPORT.md` - Detailed report on the insights endpoint fix
- `test_endpoints.py` - Python script to test all endpoints
- `src/mist_client.py` - Python client implementation

## 📄 License

This collection is part of the Mist Infrastructure Manager project.
