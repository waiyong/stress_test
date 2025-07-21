# 📊 Church Asset Risk & Stress Testing Dashboard

## 🎯 Objectives

- Quantify downside and liquidity risk of CPC’s investment portfolio.
- Simulate stress scenarios (e.g. interest rate shocks, market downturns).
- Evaluate reserve adequacy under stress (vs 12-month OPEX requirement).
- Provide interactive interface for IC members to explore risks visually.
- Base on open-source tools and free market data.

---

## 🛠️ Tech Stack

| Layer        | Tool                           | Reason                                                   |
|--------------|--------------------------------|----------------------------------------------------------|
| UI           | Streamlit                      | Simple Python-based dashboard framework                  |
| Backend      | Python (pandas, NumPy)         | For simulations, data manipulation                       |
| Charting     | Plotly / Altair                | For interactive and clear visualizations                 |
| Data Sources | MAS, yfinance, FRED            | Free public market data                                  |
| Export       | ReportLab / pandas / openpyxl  | To generate downloadable reports                         |
| Data Storage | CSV files                      | Portfolio data persistence (simple, version-controllable) |
| Hosting      | Streamlit Community Cloud       | Free GitHub-integrated hosting for multiple users        |

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

## 🌍 External Market Reference Data

| Data                         | Use                                 | Source                             |
|------------------------------|--------------------------------------|------------------------------------|
| Interest rates (SORA, FD)    | Model FD and MMF returns             | MAS                                |
| Inflation history (CPI)      | Compute real returns                 | SingStat                           |
| Historical drawdowns         | Stress equity components             | yfinance                           |
| Bond & T-bill yields         | Calibrate return benchmarks          | MAS / Investing.com (SG)           |
| FX rates                     | If portfolio includes FX exposure    | MAS                                |

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

## 📅 Project Timeline (Est. 4–6 Weeks)

| Week | Task                                                                 |
|------|----------------------------------------------------------------------|
| 1    | Define stress scenarios, collect sample data, design schema         |
| 2    | Build Python backend simulation logic                               |
| 3    | Integrate open market data APIs (MAS, yfinance)                     |
| 4    | Build Streamlit UI with tweakable sliders                           |
| 5    | Add charts and export options (CSV/PDF)                             |
| 6    | User testing with IC, gather feedback, iterate                      |

---

## 🧩 Optional Features

- Save/load past test scenarios
- Upload Excel files for actual portfolios
- Auto-report generation with timestamp & notes
- Side-by-side scenario comparison

---

## ⚠️ Limitations

- Some mutual funds do not expose real-time NAV or holdings — proxy using ETFs.
- MAS data may be delayed (not real-time).
- yfinance API has rate limits — use caching if needed.

---

## 🏗️ Data Architecture

### Portfolio Data Storage
- **File**: `portfolio.csv` - Persistent storage of investment composition
- **Structure**: Asset Type, Amount (SGD), Fund Name, Liquidity Period, Notes
- **Access**: Editable via UI or direct CSV upload/download
- **Backup**: Downloadable timestamped copies

### Market Data Flow
- **Refresh**: Weekly automatic refresh with local file caching
- **Sources**: yfinance (primary), MAS API (secondary), manual fallback
- **Storage**: Local JSON files (`data/market_cache/YYYY-MM-DD.json`)
- **Persistence**: Data survives between sessions, reduces API calls
- **Cleanup**: Automatic removal of cache files older than 2 weeks

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
│   ├── __init__.py
│   ├── risk_engine.py      # Core stress testing calculations
│   ├── data_sources.py     # Market data API integrations
│   ├── report_generator.py # PDF report creation
│   └── config.py          # Configuration constants
├── data/
│   ├── sample_portfolio.csv
│   └── market_cache/       # Temporary market data cache
└── docs/
    ├── CLAUDE.md          # Development guidance
    └── user_guide.md      # End-user documentation
```

---

## 🎯 MVP Scope & Phases

### Phase 1 - Core MVP (2-3 weeks)
- ✅ Basic portfolio input via CSV
- ✅ Core risk calculation engine (6 key metrics)
- ✅ Simple Streamlit UI with parameter sliders
- ✅ Sample/mock market data integration
- ✅ Basic PDF report generation
- ✅ Streamlit Community Cloud deployment

### Phase 2 - Enhanced Features (1-2 weeks)
- 🔄 Real market data APIs (yfinance priority)
- 🔄 Preset scenario templates (3-5 standard scenarios)
- 🔄 Enhanced visualizations and charts
- 🔄 Improved report formatting and branding

### Phase 3 - Advanced Features (Future)
- 🔮 Simple password protection
- 🔮 Historical scenario comparison
- 🔮 Advanced portfolio upload (Excel support)
- 🔮 Real-time market data integration

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

