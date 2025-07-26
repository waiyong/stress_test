# 📊 Data Management Operations Runbook

## Purpose and Overview

**Purpose**: Operational procedures for managing market data pipeline in the Church Asset Risk Dashboard  
**Audience**: System administrators, developers, and technical support staff  
**Use Cases**: Daily operations, troubleshooting data issues, performing backfills, system maintenance

**System Context**: The dashboard uses an intelligent hybrid data management system with OpenBB Platform integration, asset-based storage, and automated GitHub Actions updates.

---

## Prerequisites

Before executing any data management operations:

1. **Environment Access**:
   - [ ] Local development environment with Python 3.8+
   - [ ] Virtual environment activated: `source venv/bin/activate`
   - [ ] Repository access with latest code

2. **Permissions Required**:
   - [ ] GitHub repository write access (for manual triggers)
   - [ ] Local file system access to `data/market_cache/`
   - [ ] OpenBB Platform access (automatic via public endpoints)

3. **System Health Check**:
   ```bash
   # Verify system components
   python -c "from utils.enhanced_data_sources import get_enhanced_data_manager; print('✅ System Ready')"
   ```

---

## 🗂️ Data Storage Structure

### **Daily Data** (`current/*.json`)
**Purpose**: Hot cache for dashboard access (0.002s load time)

```
data/market_cache/current/
├── STI_current.json              # Latest STI price only
├── singapore_rates_current.json  # Current interest rates
├── SGDUSD_current.json           # Live exchange rate
└── [asset]_current.json          # Current values for immediate use
```

**Content**: Single current price + metadata
```json
{
  "current_price": 4261.06,
  "last_updated": "2025-07-26T17:26:38",
  "source_file": "STI_2025-07.json"
}
```

### **Historical Data** (`[asset-type]/[asset]_YYYY-MM.json`)
**Purpose**: Full price history + computed metrics

```
data/market_cache/
├── indices/STI_2025-07.json           # STI historical prices
├── rates/singapore_rates_2025-07.json # Rate history  
├── currencies/SGDUSD_2025-07.json     # Currency history
└── bonds/singapore_bonds_2025-07.json # Bond yield history
```

**Content**: Daily price history + risk metrics
```json
{
  "price_history": {
    "2025-07-21": {"price": 4208.26, "timestamp": "..."},
    "2025-07-22": {"price": 4215.33, "timestamp": "..."}
  },
  "computed_metrics": {
    "1y_return": 0.085,
    "1y_volatility": 0.18,
    "max_drawdown": -0.12
  }
}
```

### **Month-End Processing**
**Process**: New monthly files created automatically
- **Trigger**: First update of new month
- **Action**: Create `[asset]_YYYY-MM.json` for new month
- **Retention**: Old monthly files kept for historical analysis

---

## 🔄 Daily Operations

### 1. Monitor Automated Updates

**Frequency**: Daily  
**Trigger**: Automated via GitHub Actions (weekdays 6 PM Singapore)

#### Check Update Status:
1. **Navigate** to GitHub repository → Actions tab
2. **Verify** latest "Market Data Update" workflow succeeded
3. **Check** update summary for key metrics:
   - STI price updated
   - Data source status (OpenBB/Cache/Fallback)
   - Last update timestamp

#### Expected Outcome:
- ✅ Green checkmark on latest workflow run
- ✅ Update summary shows current market prices
- ✅ Timestamp within last 24 hours

#### If Update Failed:
→ **Escalate to**: [Troubleshooting Failed Updates](#troubleshooting-failed-updates)

### 2. Validate Data Quality

**Frequency**: Daily (after automated updates)

#### Check Data Freshness:
```bash
# Activate environment
source venv/bin/activate

# Run validation
python scripts/update_market_data.py --validate-only
```

#### Expected Outcome:
```
✅ Existing data validation passed
- STI Price: $4,261.06
- Last Update: 2025-07-26T18:00:00
- Data Age: <24 hours
```

#### If Validation Fails:
→ **Escalate to**: [Data Quality Issues](#data-quality-issues)

---

## 🛠️ Manual Operations

### 3. Incremental Update (Current Prices)

**Purpose**: Refresh current market prices without full historical data  
**Duration**: ~3 seconds  
**API Usage**: ~10 calls

#### When to Use:
- Market hours when you need latest prices
- After system maintenance
- Before important IC meetings

#### Steps:
1. **Activate** virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. **Run** incremental update:
   ```bash
   python scripts/update_market_data.py --type incremental --verbose
   ```

3. **Monitor** output for:
   - "Starting incremental market data update..."
   - "✅ Market data update completed successfully"

#### Expected Outcome:
- Current prices updated in `data/market_cache/current/`
- Dashboard shows latest market data
- No historical data changes

### 4. Full Refresh (Intelligent Hybrid)

**Purpose**: Refresh historical data with intelligent backfill logic  
**Duration**: 10-45 seconds depending on data age  
**API Usage**: 50-1000 calls depending on hybrid decision

#### What it does - Intelligent Hybrid Approach:
- 🧠 **Smart Decision**: Checks if existing historical data >180 days old
- ✅ **Full Refresh**: If data >180 days old → fetches complete history (data quality)
- ⚡ **Incremental Backfill**: If data <180 days old → fetches only missing date ranges
- ✅ Recalculates all risk metrics (volatility, returns, drawdowns)
- ✅ Updates both historical and current files

#### Performance:
- **Full Refresh** (>180 days old): ~30 seconds, 1000 API calls
- **Incremental Backfill** (<180 days old): ~10 seconds, 50 API calls

#### When to Use:
- Weekly data quality maintenance
- After detecting stale data (>48 hours)
- When adding new start date requirements
- After system errors affecting data integrity
- **Backfilling to earlier dates** with optimized API usage

#### Hybrid Logic Decision:
- **Recent data (<180 days old)**: Incremental gap filling (50 API calls, 10 seconds)
- **Stale data (>180 days old)**: Full refresh for quality (1000 API calls, 45 seconds)

#### Steps:
1. **Activate** virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. **Run** full refresh (uses default start date):
   ```bash
   python scripts/update_market_data.py --type full_refresh --verbose
   ```

3. **Monitor** decision output:
   ```
   Historical data is 45 days old (<180), using incremental backfill
   OR
   Historical data is 200 days old (>180), performing full refresh for data quality
   ```

#### Expected Outcome:
- Historical files updated in `data/market_cache/{asset_type}/`
- Current cache refreshed
- Decision logged based on data age

### 5. Custom Date Backfill

**Purpose**: Extend historical data to earlier periods  
**Risk Level**: Medium (significant API usage)

#### When to Use:
- Investment Committee requests longer historical analysis
- New stress testing scenarios requiring older data
- Compliance or audit requirements

#### Steps:
1. **Determine** required start date (e.g., 2016-01-01)

2. **Estimate** API impact:
   - **Recent data**: ~50 API calls (gap filling only)
   - **Stale data**: ~1000 API calls (complete refresh)

3. **Execute** backfill:
   ```bash
   python scripts/update_market_data.py --type full_refresh --start-date 2016-01-01 --verbose
   ```

4. **Monitor** progress:
   - Gap detection: "Incremental backfill for STI: fetching gap 2016-01-01 to 2018-01-01"
   - OR full refresh: "Full refresh for STI: fetching from 2016-01-01"

#### Expected Outcome:
- Extended historical coverage from specified date
- Minimal API usage if data is recent
- Complete dataset refresh if data is stale

### 6. GitHub Actions Manual Trigger

**Purpose**: Trigger data updates remotely via GitHub interface  
**Access Required**: GitHub repository permissions

#### When to Use:
- Remote system administration
- Scheduled maintenance outside normal hours
- Emergency data refresh

#### Via GitHub Web Interface:
1. **Navigate** to repository → Actions tab
2. **Select** "Market Data Update" workflow
3. **Click** "Run workflow" button
4. **Configure** parameters:
   - **Update Type**: `incremental` or `full_refresh`
   - **Start Date**: `2018-01-01` (for backfill)
5. **Click** "Run workflow"

#### Via GitHub CLI:
```bash
# Standard refresh
gh workflow run "Market Data Update" --field update_type=full_refresh

# Custom backfill
gh workflow run "Market Data Update" \
  --field update_type=full_refresh \
  --field start_date=2016-01-01
```

#### Expected Outcome:
- Workflow appears in Actions tab
- Data files updated and committed
- Streamlit Cloud auto-deploys updates

---

## 🧠 Intelligent Backfill Logic

### **How the Hybrid Approach Works**

When you run `full_refresh`, the system makes smart decisions to optimize API usage while maintaining data quality:

```python
# Decision Tree
if existing_historical_data_age > 180_days:
    → Full API refresh (data quality priority)
    → Fetches complete history from start_date to present
    → Overwrites all existing files
    → ~1000 API calls, 45 seconds
else:
    → Incremental backfill (efficiency priority)  
    → Checks existing data coverage: "earliest date = 2018-01-01"
    → Identifies gap: "need 2016-01-01 to 2017-12-31"
    → Fetches ONLY the missing date range
    → Preserves existing 2018-2025 data
    → ~50 API calls, 10 seconds
```

### **Why 180 Days?**

**Data Quality Considerations:**
- **Corporate actions** (stock splits, dividends) often require historical adjustments
- **Data provider changes** can create inconsistencies between old and new data
- **Schema evolution** may require complete dataset refresh
- **180 days** balances efficiency with data integrity (twice per year quality refresh)

### **Gap Detection Process**

```bash
# Example: Backfill from 2016, existing data from 2018
1. Check existing coverage: "STI: 2018-01-01 to 2025-07-26"
2. Compare with target: "Want: 2016-01-01 to present"  
3. Identify gap: "Missing: 2016-01-01 to 2017-12-31"
4. API call: fetch_historical(start="2016-01-01", end="2017-12-31")
5. Merge: Combine gap data with existing 2018+ data
6. Result: Complete 2016-2025 dataset with minimal API usage
```

---

## 📋 Common Scenarios

### **Scenario 1: Daily Operations**
**Current**: Historical data from 2018-01-01, need today's prices
```bash
# Automated daily update (GitHub Actions)
python scripts/update_market_data.py --type incremental
```
**Result**: Adds today's price to existing history, updates dashboard cache

### **Scenario 2: Backfill Historical Data**
**Current**: Historical data from 2018-01-01, need data from 2016-01-01
```bash
# Intelligent full refresh with earlier start date
python scripts/update_market_data.py --type full_refresh --start-date 2016-01-01
```
**Result - Hybrid Approach**: 
- 🧠 **Checks data age**: If existing data <180 days old:
  - ⚡ **Incremental**: Fetches only 2016-2017 gap (~50 API calls)
  - 📊 **Preserves**: Existing 2018-2025 data unchanged
- 🔄 **If data >180 days old**: Full refresh for data quality (1000 API calls)
- ⚡ Updates hot cache with latest data

### **Scenario 3: Data Quality Issues**
**Current**: Suspect data corruption or missing days
```bash
# Validate existing data
python scripts/update_market_data.py --validate-only

# If issues found, refresh current month
python scripts/update_market_data.py --type full_refresh --start-date 2025-01-01
```

### **Scenario 4: Add New Asset**
**Current**: Want to track new index (e.g., MSCI Emerging Markets)
1. Add ticker to `enhanced_data_sources.py:312`
2. Run full refresh to populate historical data
```bash
python scripts/update_market_data.py --type full_refresh
```

### **Scenario 5: GitHub Actions Manual Trigger**
**Via GitHub Web Interface:**
1. **Actions** → **Market Data Update** → **Run workflow**
2. Select: **Update Type**: `full_refresh`
3. Set: **Start Date**: `2016-01-01`
4. Click **Run workflow**

**Via GitHub CLI:**
```bash
gh workflow run "Market Data Update" \
  --field update_type=full_refresh \
  --field start_date=2016-01-01
```

---

## 🚨 Troubleshooting

### Data Quality Issues

#### Symptom: Validation fails with errors

**Common Causes**:
- API rate limits exceeded
- OpenBB Platform service issues
- Network connectivity problems
- Corrupted cache files

#### Diagnosis Steps:
1. **Check** error details:
   ```bash
   python scripts/update_market_data.py --validate-only --verbose
   ```

2. **Review** common error patterns:
   - `"Missing or empty section: singapore_rates"` → API fetch failed
   - `"Data is stale: X hours old"` → Update mechanism failed
   - `"Invalid price for index: STI=0.0"` → Data corruption

#### Resolution:
1. **For API issues**:
   ```bash
   # Force fresh data fetch
   python scripts/update_market_data.py --type full_refresh
   ```

2. **For corrupted cache**:
   ```bash
   # Remove corrupted files and refresh
   rm -rf data/market_cache/current/*
   python scripts/update_market_data.py --type full_refresh
   ```

3. **For persistent issues**:
   → **Escalate to**: Development team with full error logs

### Troubleshooting Failed Updates

#### Symptom: GitHub Actions workflow fails

**Common Causes**:
- OpenBB Platform API limits
- GitHub runner issues
- Code errors in update script
- Permission problems

#### Diagnosis Steps:
1. **Check** GitHub Actions logs:
   - Navigate to Actions → Failed workflow → View logs
   - Look for error patterns in "Run market data update" step

2. **Common error patterns**:
   - `"Failed to fetch Singapore rates"` → OpenBB API issue
   - `"No module named 'openbb'"` → Environment issue
   - `"Permission denied"` → GitHub token issue

#### Resolution:
1. **For API limits**:
   - Wait for rate limit reset (usually 24 hours)
   - Monitor OpenBB Platform status page

2. **For environment issues**:
   - Re-run workflow (often transient)
   - Check requirements.txt for dependency issues

3. **For permission issues**:
   - Verify GitHub token has workflow permissions
   - Check repository settings → Actions permissions

### Performance Issues

#### Symptom: Updates taking longer than expected

**Normal Durations**:
- Incremental update: ~3 seconds
- Hybrid refresh (recent data): ~10 seconds
- Hybrid refresh (stale data): ~45 seconds

#### If Updates Are Slow:
1. **Check** data age decision:
   ```bash
   python scripts/update_market_data.py --type full_refresh --verbose
   # Look for: "Historical data is X days old"
   ```

2. **Verify** network connectivity to OpenBB Platform

3. **Consider** API rate limiting if consistently slow

### System Health Monitoring

#### Daily Health Check Commands:
```bash
# System component check
python -c "
from utils.enhanced_data_sources import get_enhanced_data_manager
manager = get_enhanced_data_manager()
data = manager.fetch_market_data()
print('✅ System Health:', 'OK' if data.get('singapore_rates') else 'FAILED')
"

# Data freshness check
python -c "
from utils.enhanced_data_sources import get_enhanced_data_manager
manager = get_enhanced_data_manager()
age_days = manager._get_existing_data_age_days()
print(f'Data Age: {age_days} days ({'OK' if age_days < 7 else 'ATTENTION NEEDED'})')
"
```

---

## 📋 Escalation Procedures

### Level 1: Self-Service Resolution
**Duration**: 15 minutes  
**Actions**: Follow troubleshooting steps, retry operations, check logs

### Level 2: Development Team
**When to Escalate**:
- Data corruption persists after cache cleanup
- GitHub Actions consistently failing >24 hours
- API errors not resolved by waiting
- New error patterns not covered in runbook

**Required Information**:
- Error logs from failed operations
- Screenshots of GitHub Actions failures
- Output from diagnostic commands
- Description of attempted resolution steps

### Level 3: External Dependencies
**When to Escalate**:
- OpenBB Platform service outages
- GitHub platform issues
- Streamlit Cloud deployment problems

**Actions**:
- Check service status pages
- Implement fallback procedures
- Document incident for post-mortem

---

## 📊 Quick Reference

### Key Commands
| Operation | Command | Duration | API Calls |
|-----------|---------|----------|-----------|
| **Health Check** | `--validate-only` | 1 second | 0 |
| **Daily Update** | `--type incremental` | 3 seconds | 10 |
| **Weekly Refresh** | `--type full_refresh` | 10-45 seconds | 50-1000 |
| **Custom Backfill** | `--type full_refresh --start-date YYYY-MM-DD` | 10-45 seconds | 50-1000 |

### File Locations
| Data Type | Path | Purpose |
|-----------|------|---------|
| **Current Prices** | `data/market_cache/current/` | Hot cache (0.002s access) |
| **Historical Data** | `data/market_cache/{asset_type}/` | Monthly organized files |
| **System Status** | `data/market_cache/metadata/` | Health and timing info |
| **Logs** | GitHub Actions → Workflow logs | Error diagnosis |

### Decision Matrix
| Data Age | Operation Type | API Calls | Use Case |
|----------|----------------|-----------|----------|
| **<24 hours** | Skip update | 0 | Normal operations |
| **24-48 hours** | Incremental | 10 | Routine refresh |
| **48+ hours** | Full refresh | 50-1000 | Quality maintenance |
| **>180 days** | Force full refresh | 1000 | Data integrity |

---

**Document Version**: 1.2  
**Last Updated**: July 26, 2025  
**Next Review**: August 26, 2025  
**Owner**: Technical Operations Team