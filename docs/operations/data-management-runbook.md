# 📊 Data Management Runbook

## Quick Navigation
- [← Back to Documentation](../README.md)
- [Architecture Overview](../architecture/) - System design
- [Development Guide](../development/) - API reference

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

## 🔄 Data Refresh Operations

### **Incremental Update** (Default)
```bash
python scripts/update_market_data.py --type incremental
```

**What it does:**
- ✅ Fetches **current prices only** from OpenBB API
- ✅ Updates `current/*.json` files (hot cache)
- ✅ Adds today's price to monthly historical files
- ✅ **Does NOT** fetch full historical data
- ⚡ **Performance**: ~3 seconds, minimal API calls

**Use cases:**
- Daily automated updates (6 PM Singapore)
- Quick dashboard refresh
- Live price updates

### **Full Refresh** (Weekly/On-demand)
```bash
python scripts/update_market_data.py --type full_refresh --start-date 2018-01-01
```

**What it does - Intelligent Hybrid Approach:**
- 🧠 **Smart Decision**: Checks if existing historical data >180 days old
- ✅ **Full Refresh**: If data >180 days old → fetches complete history (data quality)
- ⚡ **Incremental Backfill**: If data <180 days old → fetches only missing date ranges
- ✅ Recalculates all risk metrics (volatility, returns, drawdowns)
- ✅ Updates both historical and current files

**Performance:**
- **Full Refresh** (>180 days old): ~30 seconds, 1000 API calls
- **Incremental Backfill** (<180 days old): ~10 seconds, 50 API calls

**Use cases:**
- Weekly data quality assurance
- Adding new metrics or calculations  
- **Backfilling to earlier dates** with optimized API usage

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

## ⚠️ Important Notes

### **API Usage**
- **Incremental**: ~10 API calls (current prices only)
- **Full Refresh**: ~500-1000 API calls (complete history)
- **Rate Limits**: OpenBB has daily/monthly limits

### **Data Overwrite Behavior**
- **Incremental**: Appends to existing data
- **Full Refresh (Hybrid)**:
  - **If data <180 days old**: Smart incremental (only fetches gaps, preserves existing)
  - **If data >180 days old**: Complete overwrite for data quality
- **Backup**: Old data moved to `backup_before_migration/` during major changes

### **Storage Growth**
- **Monthly Files**: ~50-200 lines per asset
- **Auto-cleanup**: Files older than 60 days removed automatically
- **Compression**: Not implemented (files are small)

### **Fallback Mechanism**
1. **Primary**: OpenBB Platform API
2. **Secondary**: Cached historical data  
3. **Tertiary**: Mock data with warnings

---

## 🛠️ Troubleshooting

### **Problem**: Stale data (>48 hours old)
**Solution**: 
```bash
python scripts/update_market_data.py --type full_refresh
```

### **Problem**: Missing historical data for specific dates
**Solution**: 
```bash
# Full refresh overwrites with complete API data
python scripts/update_market_data.py --type full_refresh --start-date 2018-01-01
```

### **Problem**: API quota exceeded  
**Solution**:
- Use cached data temporarily
- Wait for quota reset
- Dashboard continues working with fallback data

### **Problem**: Validation errors
**Solution**:
```bash
# Check data integrity
python scripts/update_market_data.py --validate-only

# Clean refresh if issues found
python scripts/update_market_data.py --type full_refresh
```

---

## 🎯 Quick Reference

| **Task** | **Command** | **API Calls** | **Duration** |
|----------|-------------|---------------|--------------|
| Daily update | `--type incremental` | ~10 | 3 seconds |
| Weekly refresh (recent data) | `--type full_refresh` | ~50 | 10 seconds |
| Weekly refresh (old data >180d) | `--type full_refresh` | ~500 | 30 seconds |
| Backfill 2016+ (recent data) | `--type full_refresh --start-date 2016-01-01` | ~50 | 10 seconds |
| Backfill 2016+ (old data >180d) | `--type full_refresh --start-date 2016-01-01` | ~1000 | 45 seconds |
| Validate only | `--validate-only` | 0 | 1 second |

**GitHub Actions**: Runs incremental updates weekdays at 6 PM Singapore automatically.

---

*This runbook covers all data management scenarios for the Church Asset Risk Dashboard. For system architecture details, see [Architecture Documentation](../architecture/).*