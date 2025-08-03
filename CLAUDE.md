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
- **Data Sources**: OpenBB Platform (professional market data), asset-based storage, CSV files
- **Reports**: ReportLab for PDF generation
- **Hosting**: Streamlit Community Cloud (free GitHub integration)
- **Storage**: CSV files for portfolio data, asset-based market data cache with automated updates

## Development Commands

### Local Development
```bash
# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application locally
streamlit run app.py

# Install additional packages (update requirements.txt after)
pip install package_name
pip freeze > requirements.txt
```

### Virtual Environment Setup
- **IMPORTANT**: Always activate the virtual environment before running any Python commands
- **Command**: `source venv/bin/activate`
- **Required for**: Running tests, installing packages, executing scripts, running Streamlit app
- **Verification**: Check that `(venv)` appears in terminal prompt

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
│   ├── enhanced_data_sources.py # OpenBB Platform integration with fallbacks
│   ├── asset_data_manager.py    # Asset-based storage management
│   ├── portfolio_performance.py # Historical performance analysis
│   ├── data_sources.py     # Legacy market data (for reference)
│   ├── report_generator.py # PDF report creation with timestamps
│   └── config.py          # Configuration constants and parameters
├── data/
│   ├── sample_portfolio.csv # Sample data for testing
│   └── market_cache/       # Asset-based market data cache
│       ├── rates/          # Singapore interest rates (monthly files)
│       ├── indices/        # Market indices (STI, MSCI, bonds)
│       ├── currencies/     # Exchange rates (SGD/USD)
│       ├── bonds/          # Government bond yields
│       ├── current/        # Hot cache for dashboard
│       └── metadata/       # Data status and monitoring
├── scripts/
│   └── update_market_data.py # Automated data update script
├── .github/workflows/
│   └── market-data-update.yml # GitHub Actions automation
└── docs/
    ├── README.md          # Main documentation hub
    ├── getting-started/   # Setup and user guides
    ├── architecture/      # Technical implementation
    ├── project-management/ # Project tracking
    └── development/       # Developer resources
```

### Core Modules

**`utils/risk_engine.py`** - Central calculation engine implementing:
- Portfolio Value Under Stress calculation
- Reserve Coverage Ratio (vs 12-month OPEX)
- Maximum Drawdown computation
- Time to Liquidity analysis
- Volatility and Liquidity breach flags

**`utils/enhanced_data_sources.py`** - Market data integration with:
- OpenBB Platform for professional-grade Singapore market data (STI, MSCI, rates, currency)
- Asset-based storage system with monthly files for optimal performance
- Intelligent refresh strategies (incremental daily, full weekly)
- Triple fallback system (OpenBB → Cache → Mock data)
- GitHub Actions automation for weekday 6 PM SGT updates

**`utils/asset_data_manager.py`** - Storage management providing:
- Asset-specific file operations (rates, indices, currencies, bonds)
- Current data aggregation for sub-second dashboard loading
- Historical data access and validation
- Automatic cleanup and maintenance

**`utils/portfolio_performance.py`** - Historical analysis with:
- 7+ years of Singapore market performance data
- Professional financial metrics (Sharpe ratios, volatility, drawdowns)
- Interactive timeline visualization with market event annotations
- Risk-return analysis and asset class comparisons

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
- **Asset-Based Storage**: Store data by asset type in monthly files (`rates/singapore_rates_2025-08.json`)
- **Intelligent Refresh**: Hybrid approach with 180-day quality threshold for optimal API usage
- **Hot Cache System**: Current data aggregated in `current/` folder for 0.002s dashboard loading
- **GitHub Actions**: Automated weekday 6 PM SGT updates with commit-based deployment
- **Triple Fallback**: OpenBB Platform → Asset Cache → Mock Data (guarantees availability)
- **Cloud Deployment**: Graceful OpenBB import handling for Streamlit Cloud permission restrictions

Example asset-based data access:
```python
from utils.enhanced_data_sources import get_enhanced_data_manager

# Initialize with automatic fallback handling
data_manager = get_enhanced_data_manager()

# Get current market data (0.002s load time)
market_data = data_manager.fetch_market_data()

# Access specific historical data
sti_history = data_manager.get_asset_history("indices", "STI", days=365)
```

### Testing Strategy:
- Use `data/sample_portfolio.csv` for consistent testing
- Test all stress scenarios with extreme parameters
- Verify PDF report generation and formatting
- Test deployment on Streamlit Community Cloud

## Documentation Structure

**Main Documentation Hub**: `docs/README.md`

The project uses a hierarchical documentation structure:

```
docs/
├── README.md                        # 🏠 Main documentation hub
├── getting-started/                 # 🚀 Setup and user guides
│   ├── README.md                   # Getting started overview
│   ├── installation.md             # Detailed installation guide
│   └── user_guide.md              # Investment Committee user manual
├── architecture/                    # 🏗️ Technical implementation
│   ├── README.md                   # Architecture overview
│   ├── dataops-implementation.md   # Asset-based storage details
│   └── openbb-integration.md       # Market data pipeline
├── project-management/              # 📋 Project tracking
│   ├── README.md                   # Project management overview
│   ├── project-plan.md            # Master roadmap
│   └── project-checkpoint.md       # Current status
└── development/                     # 🛠️ Developer resources
    ├── README.md                   # Development overview and API reference
    └── [future: deployment.md]     # Deployment procedures
```

**Navigation**: Each section README links upward to main documentation and cross-references related sections.

## Documentation Maintenance

### Architecture Diagrams
**Location**: `docs/architecture/system-diagrams.md`

**IMPORTANT**: Keep visual documentation current with code changes to ensure accuracy for stakeholders and developers.

#### When to Update Diagrams:
- **After adding new modules or components** (update High-Level Architecture, Component Interaction)
- **When changing data flow or storage architecture** (update Data Flow, Performance Architecture)
- **After modifying external integrations** (APIs, services - update Data Flow, Reliability diagrams)
- **When updating core business logic or user workflows** (update User Journey, Component Interaction)
- **After performance optimizations or architectural changes** (update Performance Architecture)
- **When changing error handling or fallback mechanisms** (update Reliability & Fallback Architecture)

#### Diagram Update Checklist:
When making architectural changes, review and update relevant diagrams:
- [ ] **High-Level System Architecture** - Overall system components and relationships
- [ ] **Data Flow Diagram** - Market data pipeline from OpenBB to dashboard
- [ ] **User Journey Flowchart** - IC member workflow through dashboard
- [ ] **Component Interaction Diagram** - Module dependencies and data flow
- [ ] **Performance Architecture** - Asset-based storage and optimization metrics
- [ ] **Reliability & Fallback Architecture** - Error handling and fallback mechanisms

#### Maintenance Schedule:
- **Immediate**: Update diagrams during architectural code reviews
- **Weekly**: Review diagram accuracy during sprint planning
- **Monthly**: Validate all diagrams reflect current system state
- **Release**: Ensure diagrams are current before major releases or IC presentations

#### Diagram Format:
- **Use Mermaid syntax** for GitHub compatibility and maintainability
- **Consistent color coding** by system layer (UI, business logic, data, external)
- **Clear annotations** for performance metrics and data flow directions
- **Version control** diagrams alongside code changes

## Deployment

### Streamlit Community Cloud (Production):
- **Repository**: Connect GitHub repo to [share.streamlit.io](https://share.streamlit.io)
- **Automatic deployment**: Push to main branch triggers deployment
- **URL format**: `https://app-name.streamlit.app`
- **Cloud compatibility**: OpenBB import handling with graceful fallback to cached data
- **Data persistence**: Asset-based cache committed to repo ensures reliable cloud deployment

### Local Development:
```bash
# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Install dependencies and run
pip install -r requirements.txt
streamlit run app.py
```

### Configuration:
- **No environment variables needed**: All configuration in `utils/config.py`
- **Portfolio data**: Persists in repository as `portfolio.csv`
- **Market data**: Environment-based path selection:
  - **Local development**: `data/market_cache/` (gitignored) - fresh OpenBB data for testing
  - **Production/Cloud**: `data/production_seed/` (committed) - minimal reliable fallback data
- **OpenBB fallback**: Graceful handling of cloud deployment permission restrictions

### Recommended .gitignore:
```
*.pyc
__pycache__/
.streamlit/
venv/
.env
```

## Current System Status

### **Production Ready** ✅
- **Technical Excellence**: 1000x performance improvement (2s → 0.002s dashboard loading)
- **Real Market Data**: Live Singapore market integration (STI, SORA rates, SGD/USD, MSCI indices)
- **Automated Operations**: GitHub Actions providing daily data updates (weekdays 6 PM SGT)
- **Cloud Deployment**: Successfully deployed on Streamlit Community Cloud
- **Risk Logic Fixes**: 4 of 7 critical issues resolved (Time Deposit sensitivity, early withdrawal penalty)

### **Outstanding Tasks** ⚠️
- **Business Validation**: Confirm OPEX assumptions (SGD 2.4M) and reserve requirements (12 months) with Investment Committee
- **Correlation Modeling**: Implement realistic crisis scenario factor correlations
- **Demo Preparation**: Review Demo_plan.md before IC presentation

## Important Notes

- **Security**: No sensitive data hardcoded; portfolio amounts are relative risk assessments for church committee
- **Performance**: Asset-based storage achieves sub-second loading; 99.64% data coverage with real-time updates
- **Reliability**: Triple fallback system (OpenBB → Asset Cache → Mock Data) guarantees system availability
- **Maintenance**: Automated daily updates via GitHub Actions; manual intervention rarely needed

## Future Enhancements

- Simple password protection for IC-only access
- Historical scenario comparison capabilities
- Excel file upload for portfolio data
- Real-time market data integration (post-MVP)