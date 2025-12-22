# API Calls Summary - Mist Infrastructure Manager

## 📊 Complete API Endpoint Inventory

This project uses **10 Mist API endpoints** across 6 functional categories.

---

## 🔍 API Calls Breakdown

### **Category 1: Authentication & Organization** (1 endpoint)

| Endpoint | Method | Purpose | File Reference |
|----------|--------|---------|----------------|
| `/self` | GET | Get user info & org privileges | `mist_client.py:65` |

**Python Code:**
```python
response = self.session.get(f"{self.BASE_URL}/self")
```

---

### **Category 2: Site Management** (1 endpoint)

| Endpoint | Method | Purpose | File Reference |
|----------|--------|---------|----------------|
| `/orgs/{org_id}/sites` | GET | List all sites in organization | `mist_client.py:86` |

**Python Code:**
```python
response = self.session.get(f"{self.BASE_URL}/orgs/{self.org_id}/sites")
```

---

### **Category 3: Device Management** (2 endpoints)

| Endpoint | Method | Purpose | File Reference |
|----------|--------|---------|----------------|
| `/orgs/{org_id}/devices` | GET | Get all org devices | `mist_client.py:109` |
| `/sites/{site_id}/devices` | GET | Get devices for specific site | `mist_client.py:107` |

**Python Code:**
```python
# Organization level
url = f"{self.BASE_URL}/orgs/{self.org_id}/devices"

# Site level
url = f"{self.BASE_URL}/sites/{site_id}/devices"
```

---

### **Category 4: SLE Metrics** (2 endpoints)

| Endpoint | Method | Purpose | File Reference |
|----------|--------|---------|----------------|
| `/sites/{site_id}/sle/site/{site_id}/metrics` | GET | Get available SLE metrics | `mist_client.py:135` |
| `/sites/{site_id}/sle/site/{site_id}/metric/{metric}/summary` | GET | Get specific metric summary | `mist_client.py:142` |

**Python Code:**
```python
# Available metrics
metrics_url = f"{self.BASE_URL}/sites/{site_id}/sle/site/{site_id}/metrics"

# Metric summary with time range
summary_url = f"{self.BASE_URL}/sites/{site_id}/sle/site/{site_id}/metric/{metric}/summary"
params = {'start': start_time, 'end': end_time}
response = self.session.get(summary_url, params=params)
```

---

### **Category 5: Insights** ✅ (2 endpoints - FIXED)

| Endpoint | Method | Purpose | File Reference | Status |
|----------|--------|---------|----------------|--------|
| `/orgs/{org_id}/insights/sites-sle` | GET | Org-level SLE insights | `mist_client.py:178` | ✅ Fixed |
| `/sites/{site_id}/insights/site/{site_id}/stats` | GET | Site-level insight stats | `mist_client.py:175` | ✅ Fixed |

**Python Code:**
```python
# Organization level (CORRECTED)
url = f"{self.BASE_URL}/orgs/{self.org_id}/insights/sites-sle"

# Site level (CORRECTED)
url = f"{self.BASE_URL}/sites/{site_id}/insights/site/{site_id}/stats"
```

**Note:** These endpoints were corrected from the original implementation. See `INSIGHTS_FIX_REPORT.md` for details.

---

### **Category 6: Alarms** ⚠️ (2 endpoints)

| Endpoint | Method | Purpose | File Reference | Status |
|----------|--------|---------|----------------|--------|
| `/orgs/{org_id}/alarms` | GET | Org-level alarms | `mist_client.py:212` | ⚠️ May 404 |
| `/sites/{site_id}/alarms` | GET | Site-level alarms | `mist_client.py:210` | ⚠️ May 404 |

**Python Code:**
```python
# Organization level
url = f"{self.BASE_URL}/orgs/{self.org_id}/alarms"

# Site level
url = f"{self.BASE_URL}/sites/{site_id}/alarms"
```

**Note:** These endpoints may return 404 if not enabled for your organization.

---

## 📁 Bruno Collection Files Created

All 10 API endpoints are now available as Bruno requests:

1. ✅ `1. Get Self.bru` - Authentication & org info
2. ✅ `2. Get Sites.bru` - Site listing
3. ✅ `3. Get Devices (All Org).bru` - Organization devices
4. ✅ `4. Get Devices (By Site).bru` - Site devices
5. ✅ `5. Get SLE Metrics (Available).bru` - Available metrics
6. ✅ `6. Get SLE Metric Summary.bru` - Metric details
7. ✅ `7. Get Insights (Org Level).bru` - Org insights (FIXED)
8. ✅ `8. Get Insights (Site Level).bru` - Site insights (FIXED)
9. ✅ `9. Get Alarms (Org Level).bru` - Org alarms
10. ✅ `10. Get Alarms (Site Level).bru` - Site alarms

---

## 🎯 Usage Statistics

| Category | # of Endpoints | Used In Module |
|----------|----------------|----------------|
| Authentication | 1 | `mist_client.py` |
| Sites | 1 | `mist_client.py`, `sle_monitor.py` |
| Devices | 2 | `mist_client.py` |
| SLE Metrics | 2 | `mist_client.py`, `sle_monitor.py` |
| Insights | 2 | `mist_client.py`, `insights_analyzer.py` |
| Alarms | 2 | `mist_client.py` |
| **TOTAL** | **10** | - |

---

## 🔐 Authentication Required

All endpoints require:

```http
Authorization: Token YOUR_API_TOKEN
Content-Type: application/json
```

Get your API token from: **Mist Portal → Organization → Settings → API Tokens**

---

## 🌍 Base URL by Region

- **EU** (default): `https://api.eu.mist.com/api/v1`
- **Global 01**: `https://api.mist.com/api/v1`
- **Global 02**: `https://api.gc1.mist.com/api/v1`
- **Global 03**: `https://api.ac2.mist.com/api/v1`

---

## 📚 Documentation Files

- **`README.md`** - Complete setup guide
- **`API_QUICK_REFERENCE.md`** - Quick endpoint reference
- **`../INSIGHTS_FIX_REPORT.md`** - Insights endpoint fix details

---

## ✅ Testing in Bruno

1. Open Bruno
2. Load collection from: `d:\coding related\mist-infra-manager\bruno`
3. Update variables in `Mist API Collection.bru`:
   - `api_token`
   - `org_id` (from request #1)
   - `site_id` (from request #2)
4. Execute requests in order (1-10)

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────┐
│ 1. Get Self                                 │
│    → Returns: org_id                        │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│ 2. Get Sites                                │
│    → Returns: site_id[]                     │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│ 3-4. Get Devices                            │
│    → Returns: device details                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 5-6. Get SLE Metrics                        │
│    → Returns: performance metrics           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 7-8. Get Insights ✅                        │
│    → Returns: SLE insights & stats          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 9-10. Get Alarms ⚠️                         │
│    → Returns: active alarms (if enabled)    │
└─────────────────────────────────────────────┘
```

---

## 🎨 Project Files Using API

| File | API Calls Used |
|------|----------------|
| `src/mist_client.py` | All 10 endpoints |
| `src/sle_monitor.py` | Sites, Devices, SLE Metrics |
| `src/insights_analyzer.py` | Insights (Org & Site) |
| `src/main.py` | Orchestrates all calls |

---

## 📊 API Coverage

- **Working**: 8/10 (80%)
- **Fixed**: 2/10 (Insights endpoints)
- **May 404**: 2/10 (Alarms endpoints)

---

**Created:** 2025-12-22  
**Project:** Mist Infrastructure Manager  
**Repository:** rockban31/mist-infra-manager
