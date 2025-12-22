# Mist API Quick Reference

## 🔑 Complete API Endpoint List

### Base URL
```
https://api.eu.mist.com/api/v1
```

### Authentication
```http
Authorization: Token YOUR_API_TOKEN
Content-Type: application/json
```

---

## 📍 All API Calls Used in This Project

### 1️⃣ User & Organization

```http
GET /self
```
Returns: User info with organization privileges

---

### 2️⃣ Sites

```http
GET /orgs/{org_id}/sites
```
Returns: Array of all sites in organization

---

### 3️⃣ Devices

**Organization Level:**
```http
GET /orgs/{org_id}/devices
```

**Site Level:**
```http
GET /sites/{site_id}/devices
```
Returns: Array of device objects

---

### 4️⃣ SLE Metrics

**List Available Metrics:**
```http
GET /sites/{site_id}/sle/site/{site_id}/metrics
```

**Get Metric Summary:**
```http
GET /sites/{site_id}/sle/site/{site_id}/metric/{metric_name}/summary?start={unix_time}&end={unix_time}
```

**Common metric_name values:**
- `time-to-connect`
- `throughput`
- `coverage`
- `capacity`
- `roaming`
- `ap-availability`

Returns: Detailed SLE data for the specific metric

---

### 5️⃣ Insights ✅ FIXED

**Organization Level:**
```http
GET /orgs/{org_id}/insights/sites-sle
```
Returns: Paginated insights data
```json
{
  "results": [...],
  "total": 3,
  "page": 1
}
```

**Site Level:**
```http
GET /sites/{site_id}/insights/site/{site_id}/stats
```
Returns: Site-specific insight statistics

---

### 6️⃣ Alarms ⚠️

**Organization Level:**
```http
GET /orgs/{org_id}/alarms
```

**Site Level:**
```http
GET /sites/{site_id}/alarms
```
Returns: Array of active alarms (may return 404 if not enabled)

---

## 🔄 Typical API Call Flow

```
1. GET /self
   ↓ (get org_id from response)
   
2. GET /orgs/{org_id}/sites
   ↓ (get site_id from response)
   
3. GET /sites/{site_id}/sle/site/{site_id}/metrics
   ↓ (get available metric names)
   
4. GET /sites/{site_id}/sle/site/{site_id}/metric/time-to-connect/summary
   ↓ (get detailed metric data)
   
5. GET /orgs/{org_id}/insights/sites-sle
   ↓ (get organization insights)
```

---

## 💡 Quick Tips

### Calculate Unix Timestamps (Python)
```python
import time
end = int(time.time())
start = end - (24 * 3600)  # 24 hours ago
```

### Calculate Unix Timestamps (JavaScript)
```javascript
const end = Math.floor(Date.now() / 1000);
const start = end - (24 * 3600);  // 24 hours ago
```

### Base URLs by Region
- **EU**: `https://api.eu.mist.com/api/v1`
- **Global 01**: `https://api.mist.com/api/v1`
- **Global 02**: `https://api.gc1.mist.com/api/v1`

---

## ⚠️ Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| 404 | Wrong endpoint | Use corrected endpoints (see INSIGHTS_FIX_REPORT.md) |
| 401 | Invalid token | Check API token is correct |
| 403 | No permissions | Verify user role has access |

---

## 📊 Response Examples

### GET /self
```json
{
  "email": "user@example.com",
  "privileges": [{
    "org_id": "d040f5f4-f098-4525-9d6d-fac1894f8113",
    "role": "admin"
  }]
}
```

### GET /orgs/{org_id}/sites
```json
[{
  "id": "ca01f9d9-cc53-4418-8762-2df3057ac968",
  "name": "Phoenix",
  "timezone": "America/Phoenix"
}]
```

### GET /sites/{site_id}/sle/site/{site_id}/metrics
```json
{
  "supported": [
    "coverage",
    "capacity",
    "time-to-connect",
    "throughput"
  ]
}
```

### GET /orgs/{org_id}/insights/sites-sle
```json
{
  "results": [
    {
      "site_id": "ca01f9d9-...",
      "type": "unknown",
      "severity": "info"
    }
  ],
  "total": 3
}
```
