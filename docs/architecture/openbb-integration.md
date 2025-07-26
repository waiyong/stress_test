# OpenBB Platform Real Financial Data Integration Plan

## Overview
Replace dummy data with real financial data from OpenBB Platform for Singapore-focused church investment portfolio stress testing.

## Phase 1: Setup & Core Data Integration (3-4 days)

### Day 1: Environment Setup
1. **Install OpenBB Platform** - Add to requirements.txt
2. **Configure API access** - Set up authentication if needed
3. **Test basic connectivity** - Verify OpenBB can fetch Singapore data

### Day 2: Data Source Development
1. **Enhance `utils/data_sources.py`** with OpenBB integration
2. **Create new functions** for each data category:
   - `get_singapore_rates()` - SORA, FD rates, govt bonds
   - `get_market_indices()` - STI, MSCI World, bond indices
   - `get_economic_indicators()` - CPI, inflation data
   - `get_volatility_data()` - Market volatility measures

### Day 3: Data Structure & Caching
1. **Design JSON storage format** for current_rates.json
2. **Implement caching logic** - daily refresh for markets, weekly for rates
3. **Add fallback mechanisms** - use existing mock data when APIs fail
4. **Create data validation** - ensure data quality and completeness

### Day 4: Testing & Validation
1. **Test all API endpoints** - verify data retrieval works
2. **Validate data formats** - ensure compatibility with risk_engine.py
3. **Test caching system** - verify persistence between sessions
4. **Document data sources** - track what comes from which provider

## Phase 2: Integration with Existing System (2-3 days)

### Day 5: Risk Engine Updates
1. **Update `utils/risk_engine.py`** to use real data instead of mock data
2. **Enhance stress testing calculations** with real historical volatility
3. **Add data source attribution** to all calculations
4. **Test stress scenarios** with real market data

### Day 6: UI & Reporting Updates
1. **Update Streamlit interface** to show real data sources and timestamps
2. **Enhance PDF reports** to include data provenance and disclaimers
3. **Add data freshness indicators** - show when data was last updated
4. **Test end-to-end workflow** from data fetch to report generation

## Data Specifications

### Target Data Sources (via OpenBB)

#### 1. Singapore Interest Rates (Daily/Weekly)
- **SORA (Singapore Overnight Rate Average)** - current and historical
- **SGD Fixed Deposit rates** - 3M, 6M, 12M tenors 
- **SGD Money Market Fund yields** - representative rates
- **SGD Government Bond yields** - 2Y, 5Y, 10Y for benchmarking

#### 2. Singapore Economic Indicators (Monthly/Quarterly)
- **Singapore CPI (Consumer Price Index)** - monthly data
- **Core inflation rate** - excluding food/energy volatility
- **MAS monetary policy decisions** - rate changes and announcements

#### 3. Multi-Asset Fund Benchmarks (Daily)
- **STI (Straits Times Index)** - local equity proxy
- **MSCI World Index** - global equity exposure
- **SGD Corporate Bond Index** - local fixed income
- **Asian High-Grade Bond Index** - regional fixed income
- **REITs Index (Singapore)** - if portfolio includes REITs

#### 4. Currency & Volatility Data (Daily)
- **SGD/USD exchange rate** - for foreign currency exposure
- **VIX or Asian volatility indices** - market fear gauge
- **Bond volatility measures** - for fixed income stress testing

#### 5. Liquidity & Market Structure Data (Weekly)
- **SGD money market spreads** - interbank vs risk-free rates
- **Repo rates** - secured funding costs
- **Bank deposit rates** - competitive landscape for FDs

### Storage Strategy

#### JSON Format for MVP
```json
{
  "date": "2025-01-15",
  "timestamp": "2025-01-15T09:30:00+08:00",
  "data_sources": {
    "rates": "OpenBB Trading Economics",
    "indices": "OpenBB Yahoo Finance",
    "economic": "OpenBB OECD"
  },
  "singapore_rates": {
    "sora": 3.25,
    "fd_3m": 3.50,
    "fd_6m": 3.75,
    "fd_12m": 4.00,
    "govt_bond_2y": 3.80,
    "govt_bond_10y": 4.20
  },
  "economic_indicators": {
    "cpi_yoy": 2.8,
    "core_inflation": 2.4,
    "mas_policy_rate": 3.25
  },
  "market_indices": {
    "sti": 3420.50,
    "sti_change_pct": -0.8,
    "msci_world": 3180.25,
    "sgd_corp_bonds": 98.45,
    "singapore_reits": 890.30
  },
  "volatility": {
    "sti_30d_vol": 18.5,
    "bond_vol": 4.2,
    "sgd_usd_vol": 8.1
  },
  "fx_rates": {
    "sgd_usd": 0.7420,
    "usd_sgd": 1.3477
  }
}
```

#### File Structure
```
data/market_cache/
├── current_rates.json          # Latest rates (overwritten daily)
├── backup/
│   ├── rates_2025-01-15.json  # Daily backups
│   └── rates_2025-01-14.json
└── historical/                 # Future: time series data
    └── market_history_2025.parquet
```

#### Refresh Schedule
- **Daily**: Market indices, SORA, volatility measures, FX rates
- **Weekly**: FD rates, money market spreads  
- **Monthly**: CPI, inflation data
- **On-demand**: Bond yields, policy rate changes

## Technical Implementation

### File Changes Required

#### 1. requirements.txt
```txt
# Add OpenBB Platform
openbb-platform>=4.0.0
```

#### 2. utils/data_sources.py - Major Enhancement
```python
import openbb as obb
from datetime import datetime, timedelta
import json
import os
import logging

# New OpenBB integration functions
def get_singapore_rates_openbb():
    """Fetch Singapore interest rates via OpenBB"""
    
def get_market_indices_openbb():
    """Fetch market indices via OpenBB"""
    
def get_economic_indicators_openbb():
    """Fetch economic indicators via OpenBB"""

# Enhanced caching system
def get_real_market_data(force_refresh=False):
    """Main function to get real market data with caching"""
    
def fallback_to_mock_data():
    """Fallback when OpenBB APIs fail"""
```

#### 3. utils/config.py - Add Configuration
```python
# OpenBB Configuration
OPENBB_CONFIG = {
    "preferred_providers": {
        "rates": "tradingeconomics",
        "indices": "yfinance", 
        "economic": "oecd"
    },
    "refresh_intervals": {
        "daily": ["indices", "volatility", "fx"],
        "weekly": ["rates", "spreads"],
        "monthly": ["economic"]
    }
}
```

#### 4. app.py - Minor UI Updates
- Add data source attribution display
- Show data freshness timestamps
- Add refresh button for manual data updates

#### 5. utils/report_generator.py - Add Attribution
- Include data source disclaimers in PDF reports
- Add data timestamp information
- Mention OpenBB Platform in methodology section

### Error Handling & Fallbacks

#### API Failure Handling
1. **Primary**: Try OpenBB with preferred providers
2. **Secondary**: Try OpenBB with alternative providers
3. **Fallback**: Use existing mock data system
4. **Logging**: Record all API failures for debugging

#### Data Validation
- Check for null/missing values
- Validate data ranges (e.g., rates between 0-20%)
- Ensure timestamps are recent
- Flag suspicious data changes

#### Rate Limiting
- Implement exponential backoff for API calls
- Cache aggressively to minimize API usage
- Respect OpenBB provider rate limits

## Success Criteria

### Phase 1 Success Metrics
- ✅ OpenBB Platform successfully installed and configured
- ✅ All 5 data categories successfully fetched from OpenBB
- ✅ JSON storage format working with proper caching
- ✅ Fallback to mock data when APIs unavailable
- ✅ Data validation preventing bad data from breaking calculations

### Phase 2 Success Metrics
- ✅ Stress testing calculations work with real data
- ✅ Streamlit UI shows real data sources and timestamps
- ✅ PDF reports include proper data source attribution
- ✅ No breaking changes to existing functionality
- ✅ End-to-end workflow from data fetch to report generation

## Risk Mitigation

### Technical Risks
- **API Failures**: Keep existing mock data system as complete fallback
- **Data Quality**: Implement comprehensive validation and anomaly detection
- **Performance**: Cache aggressively, minimize API calls during user sessions
- **Dependencies**: Pin OpenBB version to prevent breaking changes

### Business Risks
- **Data Accuracy**: Include disclaimers about data sources and limitations
- **Availability**: Multiple fallback mechanisms ensure dashboard always works
- **Cost**: Monitor API usage to stay within free tier limits
- **Compliance**: Ensure data usage complies with provider terms of service

## Future Enhancements (Post-MVP)

### Advanced Data Storage
- Switch to Parquet format for historical time series
- Implement SQLite for complex queries
- Add data compression and archival policies

### Enhanced Analytics
- Historical scenario replication using real market data
- Correlation analysis between different asset classes
- Advanced volatility modeling with GARCH

### Real-time Features
- WebSocket connections for live market data
- Real-time stress testing during market hours
- Alert system for significant market movements

## Documentation Updates Required

1. **CLAUDE.md** - Update data sources section
2. **Project_plan.md** - Mark Phase 2 as completed
3. **user_guide.md** - Document new data attribution features
4. **README.md** - Update installation instructions for OpenBB

---

*This plan ensures a smooth transition from dummy data to real financial data while maintaining system reliability and user experience.*