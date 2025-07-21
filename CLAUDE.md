# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Church Asset Risk & Stress Testing Dashboard** built for CPC's Investment Committee. The application provides interactive stress testing capabilities for the church's investment portfolio, allowing IC members to simulate various risk scenarios and evaluate reserve adequacy.

**Key Objectives:**
- Quantify downside and liquidity risk of investment portfolio
- Simulate stress scenarios (interest rate shocks, market downturns, liquidity freezes)
- Evaluate reserve adequacy vs 12-month OPEX requirement
- Generate timestamped PDF reports for committee review
- Provide accessible web interface for IC members

## Tech Stack

- **Framework**: Streamlit (main UI framework)
- **Backend**: Python with pandas, NumPy for data manipulation
- **Visualization**: Plotly for interactive charts
- **Data Sources**: yfinance (market data), MAS API (Singapore rates), CSV files
- **Reports**: ReportLab for PDF generation
- **Hosting**: Streamlit Community Cloud (free GitHub integration)
- **Storage**: CSV files for portfolio data, session caching for market data

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application locally
streamlit run app.py

# Install additional packages (update requirements.txt after)
pip install package_name
pip freeze > requirements.txt
```

### Testing with Sample Data
```bash
# Use sample portfolio for testing
cp data/sample_portfolio.csv portfolio.csv

# Test with mock market data when APIs are unavailable
# (functionality built into data_sources.py)
```

## File Structure & Key Components

```
stress_testing/
├── app.py                  # Main Streamlit application entry point
├── portfolio.csv           # Persistent portfolio data (CSV format)
├── requirements.txt        # Python dependencies
├── utils/
│   ├── risk_engine.py      # Core stress testing calculations and metrics
│   ├── data_sources.py     # Market data API integrations (yfinance, MAS)
│   ├── report_generator.py # PDF report creation with timestamps
│   └── config.py          # Configuration constants and parameters
├── data/
│   ├── sample_portfolio.csv # Sample data for testing
│   └── market_cache/       # Temporary market data cache
└── docs/
    └── user_guide.md      # End-user documentation
```

### Core Modules

**`utils/risk_engine.py`** - Central calculation engine implementing:
- Portfolio Value Under Stress calculation
- Reserve Coverage Ratio (vs 12-month OPEX)
- Maximum Drawdown computation
- Time to Liquidity analysis
- Volatility and Liquidity breach flags

**`utils/data_sources.py`** - Market data integration with:
- yfinance for historical market data and ETF proxies
- MAS API for Singapore interest rates (SORA, FD rates)
- Local file caching system (`data/market_cache/YYYY-MM-DD.json`)
- Weekly refresh with persistent storage between sessions
- Fallback to mock data when APIs unavailable

**`utils/report_generator.py`** - PDF report generation:
- Executive summary with key risk metrics
- Detailed scenario parameters and assumptions
- Risk flags and breach notifications
- Timestamped naming: `CPC_StressTest_YYYY-MM-DD_HH-MM.pdf`

## Portfolio Data Structure

**`portfolio.csv` format:**
```csv
Asset_Type,Amount_SGD,Fund_Name,Liquidity_Period_Days,Notes
Time_Deposit,500000,DBS 12M FD,365,Fixed rate 2.8%
MMF,300000,Fullerton SGD MMF,1,Variable rate
Multi_Asset,200000,Nikko AM Global Multi-Asset,30,Mixed allocation
```

## Risk Calculation Methodology

### Key Metrics Computed:
1. **Portfolio Value Under Stress**: Apply shock factors to each asset class
2. **Reserve Coverage Ratio**: (Stressed Portfolio Value) / (12-month OPEX)
3. **Maximum Drawdown**: Worst-case portfolio decline percentage
4. **Time to Liquidity**: Days to access funds under stress conditions
5. **Breach Flags**: Binary alerts for volatility >20% or inadequate reserves

### Stress Test Parameters:
- Interest Rate Shock: -2% to +2% on deposit/MMF rates
- Inflation Spike: 2% to 8% annual CPI increase
- Multi-Asset Fund Drawdown: -10% to -50% crash scenarios
- Redemption Freeze: 0 to 30 days additional liquidity delay
- Early Withdrawal Penalty: 0% to -3% on premature FD withdrawals

## Development Workflow

### Adding New Features:
1. Implement core logic in appropriate `utils/` module
2. Add UI components in `app.py` using Streamlit widgets
3. Test with sample data before integrating live market data
4. Update report generation to include new metrics
5. Test end-to-end workflow including PDF export

### Market Data Integration:
- **Local File Caching**: Store API responses in `data/market_cache/YYYY-MM-DD.json`
- **Cache Logic**: Check for today's cache file, fetch if missing or >7 days old
- **File Structure**: `{"yfinance": {...}, "mas_rates": {...}, "timestamp": "..."}`
- **Cleanup**: Auto-remove cache files older than 2 weeks on startup
- **Fallback**: Use mock data when APIs fail, log warnings appropriately
- **Rate Limits**: Respect API limits with exponential backoff

Example caching implementation:
```python
def get_cached_data(cache_date=None):
    if cache_date is None:
        cache_date = datetime.now().strftime("%Y-%m-%d")
    
    cache_file = f"data/market_cache/{cache_date}.json"
    
    if os.path.exists(cache_file):
        # Check if cache is still valid (< 7 days)
        cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if cache_age.days < 7:
            return load_json(cache_file)
    
    # Fetch fresh data and cache it
    fresh_data = fetch_from_apis()
    save_json(cache_file, fresh_data)
    cleanup_old_cache_files()
    return fresh_data
```

### Testing Strategy:
- Use `data/sample_portfolio.csv` for consistent testing
- Test all stress scenarios with extreme parameters
- Verify PDF report generation and formatting
- Test deployment on Streamlit Community Cloud

## Deployment

### GitHub Integration:
- Push to GitHub repository
- Connect to Streamlit Community Cloud
- Automatic deployment on push to main branch
- URL format: `https://app-name.streamlit.app`

### Configuration:
- No environment variables needed for MVP
- All configuration in `utils/config.py`
- Portfolio data persists in repository as `portfolio.csv`
- Cache files in `data/market_cache/` should be `.gitignore`d (temporary data)

### Recommended .gitignore:
```
data/market_cache/
*.pyc
__pycache__/
.streamlit/
```

## Important Notes

- **Security**: No sensitive data should be hardcoded; portfolio amounts are relative risk assessments
- **Performance**: Market data is cached weekly; recalculations are fast for UI responsiveness
- **Reliability**: Built-in fallbacks for when external APIs are unavailable
- **Maintenance**: Weekly market data refresh cycle; manual updates as needed

## Future Enhancements

- Simple password protection for IC-only access
- Historical scenario comparison capabilities
- Excel file upload for portfolio data
- Real-time market data integration (post-MVP)