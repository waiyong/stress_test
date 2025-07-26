# 📊 Church Asset Risk & Stress Testing Dashboard

## 🎯 Objectives

- ✅ Quantify downside and liquidity risk of CPC's investment portfolio.
- ✅ Simulate stress scenarios (e.g. interest rate shocks, market downturns).
- ✅ Evaluate reserve adequacy under stress (vs 12-month OPEX requirement).
- ✅ Provide interactive interface for IC members to explore risks visually.
- ✅ Integrate real market data via OpenBB Platform with automated operations.

---

## 🛠️ Tech Stack

| Layer        | Tool                           | Status | Reason                                                   |
|--------------|--------------------------------|--------|----------------------------------------------------------|
| UI           | Streamlit                      | ✅ | Simple Python-based dashboard framework                  |
| Backend      | Python (pandas, NumPy)         | ✅ | For simulations, data manipulation                       |
| Charting     | Plotly / Altair                | ✅ | For interactive and clear visualizations                 |
| Data Sources | OpenBB Platform                | ✅ | Professional financial data platform with 100+ providers |
| DataOps      | Asset-Based Storage + GitHub Actions | ✅ | Automated daily updates with intelligent caching     |
| Export       | ReportLab / pandas / openpyxl  | ✅ | To generate downloadable reports                         |
| Data Storage | CSV files + Asset Cache        | ✅ | Portfolio data persistence + optimized market data       |
| Hosting      | Streamlit Community Cloud       | 🔄 | Free GitHub-integrated hosting for multiple users        |

---

## 📊 Internal Data Required

| Data                    | Description                                             | Source         |
|-------------------------|---------------------------------------------------------|----------------|
| Portfolio breakdown     | % in Time Deposit, MMF, Multi-Asset Funds, etc.        | Treasurer / IC |
| Total investment value  | Current dollar amount in each category                 | Treasurer      |
| Liquidity profile       | Withdrawal period for each instrument                  | Treasurer      |
| Annual OPEX budget      | For computing reserve coverage                         | Finance Comm   |
| Fund names              | To map proxy indices or funds for stress modeling      | Treasurer      |

---

## 🌍 External Market Reference Data (✅ IMPLEMENTED)

| Data                         | Use                                 | Source                             | Status |
|------------------------------|--------------------------------------|------------------------------------|---------| 
| Interest rates (SORA, FD)    | Model FD and MMF returns             | OpenBB Platform → Asset Storage    | ✅ Real Data |
| Historical market data       | Stress equity/bond components (2020-present) | OpenBB Platform            | ✅ 5,591 Data Points |
| Market indices               | STI, MSCI World, MSCI Asia, Global Bonds | OpenBB Platform                     | ✅ Live + Historical |
| Currency rates               | SGD/USD exchange for conversions    | OpenBB Platform (Real-time)        | ✅ Live Rates |
| Bond & T-bill yields         | Calibrate return benchmarks          | OpenBB Platform (Singapore data)   | ✅ Gov't Bonds |

---

## ⚠️ Stress Test Inputs (User-Tweakable)

| Factor                          | Description                                | Default Range       |
|---------------------------------|--------------------------------------------|----------------------|
| Interest Rate Shock (%)         | Drop or rise in deposit/MMF rates          | -2% to +2%           |
| Inflation Spike (%)             | Annual CPI increase                        | 2% to 8%             |
| Multi-Asset Fund Drawdown (%)   | Simulated crash scenario                   | -10% to -50%         |
| Redemption Freeze Extension     | Liquidity delay on funds/MMFs             | 0 to 30 days         |
| Early Withdrawal Penalty (%)    | Loss on FD if withdrawn early              | 0% to -3%            |
| Counterparty Risk Shock         | Simulated asset freeze or partial writeoff | Binary or % loss     |

---

## 📈 Risk Metrics

- **Portfolio Value Under Stress**
- **Reserve Coverage Ratio** (vs 12-month OPEX)
- **Maximum Drawdown**
- **Time to Liquidity**
- **Volatility Breach Flag** (if >20% drop)
- **Liquidity Breach Flag** (if reserve fails)

---

## 📅 Project Timeline & Implementation Status

| Phase | Task                                                                 | Status |
|-------|----------------------------------------------------------------------|--------|
| **Phase 1 - MVP** | Define stress scenarios, collect sample data, design schema         | ✅ Complete |
| | Build Python backend simulation logic                               | ✅ Complete |
| | Build Streamlit UI with tweakable sliders                           | ✅ Complete |
| | Add charts and export options (CSV/PDF)                             | ✅ Complete |
| **Phase 2 - DataOps** | Integrate OpenBB Platform for real market data                     | ✅ Complete |
| | Implement asset-based storage architecture                          | ✅ Complete |
| | Build automated GitHub Actions pipeline                             | ✅ Complete |
| | Deploy real data system with 5,591 historical data points          | ✅ Complete |
| **Phase 3 - Deployment** | Update Streamlit app to use enhanced data sources                   | 🔄 In Progress |
| | Production testing with IC members                                   | 📋 Pending |
| | Streamlit Community Cloud deployment                                 | 📋 Pending |

---

## 🧩 Optional Features

- Save/load past test scenarios
- Upload Excel files for actual portfolios
- Auto-report generation with timestamp & notes
- Side-by-side scenario comparison

---

## ⚠️ Limitations

- Some mutual funds do not expose real-time NAV or holdings — proxy using ETFs and indices.
- MAS data may be delayed (not real-time) — integrated via OpenBB Platform.
- OpenBB Platform may have provider-specific rate limits — mitigated by caching and multiple fallback providers.
- Historical data from 2020 onwards may not capture all historical market cycles (pre-2008 crisis data not included).

---

## 🏗️ Data Architecture

### Portfolio Data Storage
- **File**: `portfolio.csv` - Persistent storage of investment composition
- **Structure**: Asset Type, Amount (SGD), Fund Name, Liquidity Period, Notes
- **Access**: Editable via UI or direct CSV upload/download
- **Backup**: Downloadable timestamped copies

### Market Data Flow (✅ ENHANCED DATAOPS)
- **Historical Period**: 2020-present (5+ years including COVID period)
- **Architecture**: Asset-based storage (rates/indices/currencies/bonds)
- **Updates**: Automated GitHub Actions (weekdays 6PM Singapore, incremental daily)
- **Sources**: OpenBB Platform (100+ providers) with comprehensive fallbacks
- **Storage**: Asset-specific files (`data/market_cache/{asset_type}/{asset}_{date}.json`)
- **Performance**: 1000x improvement (2+ seconds → 0.002 seconds load time)
- **Reliability**: Multi-layer fallbacks (OpenBB → Cache → Mock data)

### Report Generation
- **Output**: Timestamped PDF reports with scenario parameters
- **Naming**: `CPC_StressTest_YYYY-MM-DD_HH-MM.pdf`
- **Content**: Executive summary, detailed metrics, risk flags, assumptions

---

## 📁 File Structure

```
stress_testing/
├── app.py                  # Main Streamlit application
├── portfolio.csv           # Persistent portfolio data
├── requirements.txt        # Python dependencies
├── utils/
│   ├── risk_engine.py      # Core stress testing calculations
│   ├── data_sources.py     # Legacy market data (for reference)
│   ├── enhanced_data_sources.py # ✅ OpenBB Platform integration
│   ├── asset_data_manager.py    # ✅ Asset-based storage manager
│   ├── report_generator.py # PDF report creation
│   └── config.py          # Configuration constants
├── scripts/
│   └── update_market_data.py    # ✅ Automated data update script
├── .github/workflows/
│   └── market-data-update.yml   # ✅ GitHub Actions automation
├── data/
│   ├── sample_portfolio.csv
│   └── market_cache/       # ✅ Asset-based storage structure
│       ├── rates/          # Singapore interest rates
│       ├── indices/        # Market indices (STI, MSCI, etc.)
│       ├── currencies/     # Exchange rates
│       ├── bonds/          # Government bond yields
│       ├── current/        # Hot cache for dashboard
│       └── metadata/       # System status tracking
└── docs/
    ├── CLAUDE.md          # Development guidance
    ├── user_guide.md      # End-user documentation
    ├── project_checkpoint.md     # ✅ Implementation status
    ├── dataops_implementation_summary.md # ✅ Technical guide
    └── openbb_integration_plan.md        # ✅ Integration planning
```

---

## 🎯 Implementation Phases & Current Status

### Phase 1 - Core MVP ✅ COMPLETE
- ✅ Basic portfolio input via CSV
- ✅ Core risk calculation engine (6 key metrics)
- ✅ Simple Streamlit UI with parameter sliders
- ✅ Sample/mock market data integration
- ✅ Basic PDF report generation
- ✅ Local development environment

### Phase 2 - DataOps Infrastructure ✅ COMPLETE
- ✅ **Real market data APIs** (OpenBB Platform integration with 100+ providers)
- ✅ **Historical data** (2020-present: 5,591 real data points including COVID)
- ✅ **Asset-based storage** (1000x performance improvement: 2s → 0.002s)
- ✅ **Automated pipeline** (GitHub Actions for weekday 6PM Singapore updates)
- ✅ **Enhanced data management** (incremental updates, validation, fallbacks)
- ✅ **Production-grade reliability** (comprehensive error handling & monitoring)

### Phase 3 - Production Deployment 🔄 IN PROGRESS
- 🔄 **Dashboard integration** (Update Streamlit app with enhanced data sources)
- 📋 **End-to-end testing** (Data fetch → Dashboard → PDF report validation)
- 📋 **Streamlit Community Cloud deployment** (IC-ready production system)
- 📋 **Investment Committee rollout** (Real data dashboard for committee use)

### Phase 4 - Advanced Features 📋 PLANNED
- 📋 Simple password protection for IC access
- 📋 Historical scenario comparison capabilities  
- 📋 Advanced portfolio upload (Excel support)
- 📋 Advanced analytics (Monte Carlo, correlation analysis)

---

## 🚀 Deployment Strategy

### Development
- **Local**: `streamlit run app.py`
- **Environment**: Python 3.8+ with requirements.txt
- **Testing**: Manual testing with sample portfolio data

### Production
- **Platform**: Streamlit Community Cloud (free tier)
- **Repository**: GitHub public/private repository
- **URL**: Custom streamlit.app subdomain
- **Access**: Link sharing (password protection in Phase 3)

### Maintenance
- **Market Data**: Weekly refresh cycle
- **Updates**: GitHub-based continuous deployment
- **Monitoring**: Streamlit built-in analytics

